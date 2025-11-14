In /etc/systemd/system/people-counting.service:
---

[Unit]
Description=Camera uploader

[Service]
Type=simple
ExecStart=/usr/bin/python3 /home/connormckinnis/Desktop/People-Counting/main.py
WorkingDirectory=/home/connormckinnis/Desktop/People/Counting
Restart=always
RestartSec=5
User=pi

ExecStartPre=/bin/sleep 5

[Install]
WantedBy=multi-user.target

---


To create and start the system service: 
sudo systemctl daemon-reload
sudo systemctl enable people-count.service
sudo systemctl start people-count.service
