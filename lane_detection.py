import cv2 as cv
import numpy as np

from example import warper


def fit_lines(binary):
    height, width = binary.shape
    histogram = binary[height // 2:].sum(axis=0)
    left = np.argmax(histogram[50:width // 2]) + 50
    right = np.argmax(histogram[width // 2:width - 30]) + width // 2
    ys, xs = binary.nonzero()
    left_pixels, right_pixels = [], []
    margin = 55
    fit_image = cv.cvtColor(binary * 255, cv.COLOR_GRAY2BGR)

    for window in range(9):
        low = height - (window + 1) * height // 9
        high = height - window * height // 9
        for center, pixels in ((left, left_pixels), (right, right_pixels)):
            indices = np.flatnonzero((ys >= low) & (ys < high) &
                                     (xs >= center - margin) & (xs < center + margin))
            pixels.append(indices)
            cv.rectangle(fit_image, (int(center - margin), low),
                         (int(center + margin), high), (0, 150, 0), 1)
        if len(left_pixels[-1]) > 30:
            left = int(np.median(xs[left_pixels[-1]]))
        if len(right_pixels[-1]) > 30:
            right = int(np.median(xs[right_pixels[-1]]))

    fits = []
    for pixels, color in ((left_pixels, (0, 0, 255)), (right_pixels, (255, 0, 0))):
        indices = np.concatenate(pixels)
        if len(indices) < 100 or np.ptp(ys[indices]) < height * .3:
            return None, fit_image
        x, y = xs[indices], ys[indices]
        fit = np.polyfit(y, x, 2)
        for _ in range(3):
            distance = np.abs(x - np.polyval(fit, y))
            keep = distance < max(6, min(30, 3 * np.median(distance)))
            if keep.sum() < 100:
                return None, fit_image
            x, y = x[keep], y[keep]
            fit = np.polyfit(y, x, 2)
        fit_image[y, x] = color
        fits.append(fit)

    y = np.linspace(height * .2, height * .95, 10)
    width_at_y = np.polyval(fits[1], y) - np.polyval(fits[0], y)
    if np.any(width_at_y < width * .3) or np.any(width_at_y > width * .72):
        return None, fit_image
    if np.ptp(width_at_y) > width * .22:
        return None, fit_image
    return fits, fit_image


def process_frame(img, mtx, dist, previous=None, save_steps=False):
    undistorted = cv.undistort(img, mtx, dist, None, mtx)
    work = cv.resize(undistorted, (640, 360), interpolation=cv.INTER_AREA)
    hls = cv.cvtColor(work, cv.COLOR_BGR2HLS)
    lab = cv.cvtColor(work, cv.COLOR_BGR2LAB)
    hue, light, saturation = cv.split(hls)
    b, g, r = cv.split(work)
    blur = cv.GaussianBlur(light, (3, 3), 0)
    contrast = cv.morphologyEx(blur, cv.MORPH_TOPHAT, np.ones((1, 25), np.uint8))

    yellow = cv.inRange(hls, np.array([12, 0, 70]), np.array([40, 255, 255])) > 0
    yellow &= (lab[:, :, 2] >= 142) & (r > 85) & (g > 70)
    _, bright = cv.threshold(light, 109, 255, cv.THRESH_BINARY)
    white = (bright > 0) & (saturation < 110) & (contrast >= 22)
    sobelX = cv.Sobel(blur, cv.CV_32F, 1, 0, ksize=3)
    gradient = ((np.abs(sobelX) >= 40) & (np.abs(sobelX) <= 220) &
                (contrast >= 18) & (saturation < 110) & (light >= 120))

    mask = np.zeros(light.shape, np.uint8)
    cv.fillPoly(mask, [np.int32([[26, 344], [256, 205], [378, 205], [614, 344]])], 255)
    binary = cv.bitwise_and(np.uint8(yellow | white | gradient), mask)
    binary = cv.morphologyEx(binary, cv.MORPH_CLOSE, np.ones((3, 3), np.uint8))

    src = np.float32([[585, 460], [695, 460], [1127, 720], [203, 720]]) / 2
    dst = np.float32([[160, 0], [480, 0], [480, 359], [160, 359]])
    warped = warper(binary, src, dst)
    fits, fit_image = fit_lines(warped)
    result = undistorted.copy()

    if fits is not None:
        if previous is not None:
            fits = [.3 * current + .7 * old for current, old in zip(fits, previous)]
        y = np.arange(65, 342)
        left = np.column_stack((np.polyval(fits[0], y), y)).astype(np.int32)
        right = np.column_stack((np.polyval(fits[1], y), y)).astype(np.int32)
        polygon = np.vstack((left, right[::-1]))
        lane = np.zeros((360, 640, 3), np.uint8)
        cv.fillPoly(lane, [polygon], (0, 180, 0))
        cv.polylines(lane, [left, right], False, (0, 255, 255), 3)
        inverse = cv.getPerspectiveTransform(dst, src)
        lane = cv.warpPerspective(lane, inverse, (640, 360))
        lane = cv.resize(lane, (img.shape[1], img.shape[0]))
        result = cv.addWeighted(result, 1, lane, .4, 0)

        y_eval = .92 * 360
        left_x, right_x = [np.polyval(fit, y_eval) for fit in fits]
        xm, ym = 3.7 / (right_x - left_x), 30 / 360
        center_fit = (fits[0] + fits[1]) / 2
        a, b = center_fit[0] * xm / ym**2, center_fit[1] * xm / ym
        radius = (1 + (2 * a * y_eval * ym + b)**2)**1.5 / (2 * abs(a)) if abs(a) > 1e-8 else np.inf
        matrix = cv.getPerspectiveTransform(src, dst)
        vehicle_x = cv.perspectiveTransform(np.float32([[[320, 359]]]), matrix)[0, 0, 0]
        offset = (vehicle_x - (left_x + right_x) / 2) * xm
        text = f'Curvature: {radius:.0f} m' if radius < 10000 else 'Curvature: approximately straight'
        cv.putText(result, text, (25, 40), cv.FONT_HERSHEY_SIMPLEX, .9, (255, 255, 255), 2)
        side = 'right' if offset > 0 else 'left'
        cv.putText(result, f'Vehicle: {abs(offset):.2f} m {side} of center', (25, 80),
                   cv.FONT_HERSHEY_SIMPLEX, .9, (255, 255, 255), 2)
        for fit in fits:
            points = np.column_stack((np.polyval(fit, y), y)).astype(np.int32)
            cv.polylines(fit_image, [points], False, (0, 255, 255), 2)
    else:
        cv.putText(result, 'Lane not detected', (25, 40), cv.FONT_HERSHEY_SIMPLEX,
                   .9, (0, 0, 255), 2)

    if save_steps:
        cv.imwrite('outputs/images/test2/undistorted.jpg', undistorted)
        cv.imwrite('outputs/images/test2/binary.png', binary * 255)
        cv.imwrite('outputs/images/test2/warped.png', warped * 255)
        cv.imwrite('outputs/images/test2/fit.jpg', fit_image)
        cv.imwrite('outputs/images/test2/result.jpg', result)
    return result, fits
