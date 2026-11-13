# EC2 Practice App

HTML + CSS + JS frontend, FastAPI backend, SQLite storage.
FastAPI serves the frontend too, so it's one app to deploy.

## Run locally

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open http://127.0.0.1:8000 (API docs: /docs)

## Deploy on AWS EC2 (Ubuntu)

### 1. Launch the instance
- AMI: Ubuntu 22.04/24.04, type: t2.micro / t3.micro (free tier)
- Create/download a key pair (.pem)
- Security group inbound rules: SSH (22) from My IP, HTTP (80) from anywhere

### 2. Connect
```bash
chmod 400 your-key.pem
ssh -i your-key.pem ubuntu@<EC2_PUBLIC_IP>
```

### 3. Install packages
```bash
sudo apt update
sudo apt install -y python3-venv python3-pip nginx
```

### 4. Copy the project (from your local machine)
```bash
scp -i your-key.pem -r ec2-practice-app ubuntu@<EC2_PUBLIC_IP>:/home/ubuntu/
```
(or `git clone` your repo on the server)

### 5. Set up the app (on EC2)
```bash
cd ~/ec2-practice-app
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 6. Run as a service
```bash
sudo cp deploy/fastapi.service /etc/systemd/system/fastapi.service
sudo systemctl daemon-reload
sudo systemctl enable --now fastapi
sudo systemctl status fastapi
```

### 7. Nginx reverse proxy
```bash
sudo cp deploy/nginx.conf /etc/nginx/sites-available/fastapi
sudo ln -s /etc/nginx/sites-available/fastapi /etc/nginx/sites-enabled/
sudo rm /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl restart nginx
```

Visit `http://<EC2_PUBLIC_IP>`.

## Useful commands
```bash
sudo journalctl -u fastapi -f        # app logs
sudo systemctl restart fastapi       # after code changes
sudo tail -f /var/log/nginx/error.log
```

## Next things to practice
- Elastic IP (static IP), then a domain via Route 53
- HTTPS with certbot: `sudo apt install certbot python3-certbot-nginx && sudo certbot --nginx`
- Swap SQLite for RDS (PostgreSQL)
- CI/CD with GitHub Actions deploying over SSH
"# fastapi-todo-app" 
