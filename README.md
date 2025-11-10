In /etc/systemd/system/people-count.service:
---

[Unit]
Description=People Counting Script

[Service]
ExecStart=/home/pi/venv/bin/python /home/pi/Desktop/People-Counting/main.py
WorkingDirectory=/home/pi/Desktop/People-Counting
StandardOutput=journal
StandardError=journal
Restart=always
User=pi

[Install]
WantedBy=multi-user.target

---


To create and start the system service: 
sudo systemctl daemon-reload
sudo systemctl enable people-count.service
sudo systemctl start people-count.service
