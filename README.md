# Detekcija saobraćajne trake

Program obrađuje `project_video03.mp4` i prikazuje granice trake, zelenu
površinu između njih, približnu krivinu i bočni položaj vozila.

## Instalacija i pokretanje (Ubuntu 24.04)

Potreban je Python 3.12 ili noviji. Komande instaliraju Python, Git i FFmpeg,
preuzimaju projekat i instaliraju NumPy i OpenCV u lokalno Python okruženje.
FFmpeg paket uključuje i ffprobe.

```bash
sudo apt update
sudo apt install -y git python3 python3-venv ffmpeg

git clone https://github.com/pavlemaruna/projekat_master_multimedija.git
cd projekat_master_multimedija

python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python run_project.py
```

Otvaranje dobijenog videa:

```bash
xdg-open outputs/videos/project_video03/project_video03_output.mp4
```

Za svako naredno pokretanje, iz foldera projekta:

```bash
.venv/bin/python run_project.py
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
