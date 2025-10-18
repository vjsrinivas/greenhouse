sudo systemctl daemon-reload
sudo cp greenhouse.service /etc/systemd/system/
sudo systemctl enable greenhouse.service
sudo systemctl start greenhouse.service
sudo systemctl daemon-reload
