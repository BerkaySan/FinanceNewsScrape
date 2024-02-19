sudo docker build -t eksi_scrape_img .
sudo docker-compose up selenium-hub
sudo docker-compose up chrome
sudo docker-compose up eksi_app

# diğer bilgisayarda çalıştırırken ip kontrolü yap !!!
