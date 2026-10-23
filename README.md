# Detekcija saobraćajne trake

Program obrađuje `project_video03.mp4` i prikazuje granice trake, zelenu
površinu između njih, približnu krivinu i bočni položaj vozila.

Potrebni su Python, NumPy, OpenCV, FFmpeg i ffprobe.

```bash
cd /home/pmaruna/projekat_master_multimedija
.venv/bin/python run_project.py
```

Za novo Python okruženje:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
```

## Fajlovi

- `calibration.py` — kalibracija iz fotografija šahovske table.
- `example.py` — zadata funkcija `warper` za perspektivnu transformaciju.
- `lane_detection.py` — boje, gradijenti, maska puta, polinomi, krivina i prikaz.
- `run_project.py` — učitavanje parametara, obrada jednog videa i zapisivanje MP4.

Ulazi: `calibration1.jpg`–`calibration20.jpg`, `test2.jpg` i `project_video03.mp4`.
Kalibracija se automatski izvršava ako ne postoji `outputs/calibration/calib.npz`.
Za ponovno računanje parametara pokrenuti `.venv/bin/python calibration.py`.

Slika `test2.jpg` služi samo za prikaz međukoraka zahtevanih zadatkom.
Ostale slike i filmovi se ne obrađuju.

## Rezultat

[Izlazni video](outputs/videos/project_video03/project_video03_output.mp4)

[Izveštaj](writeup.md)

Metričke procene pretpostavljaju širinu trake 3,7 m i uzdužnu skalu 30 m.
