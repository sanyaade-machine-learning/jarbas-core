cd ~
git clone https://github.com/Picovoice/Porcupine
cd Porcupine
sudo pip install -r requirements.txt
export PYTHONPATH="${PYTHONPATH}:./binding/python/"