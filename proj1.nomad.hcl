job "scraping-job" {
  datacenters = ["dc1"]

  group "selenium-hub" {
    network { mode = "host" }
    task "selenium-hub" {
      driver = "docker"
      config {
        image        = "selenium/hub:3.141.59-20201010"
        network_mode = "host"
      }
    }
  }

  group "selenium-nodes" {
    count = 2
    network {
      mode = "host"
      port "http" {}
    }
    task "selenium-node" {
      driver = "docker"
      env {
        HUB_HOST = "localhost"
        SE_OPTS  = "-port ${NOMAD_PORT_http}"
      }
      config {
        network_mode = "host"
        image        = "selenium/node-chrome:3.141.59-20201010"
      }
    }
  }

  group "eksi_app" {
    service {
      name = "eksi-app"
      port = "http"
    }
    network {
      mode = "bridge"
      port "http" {
        to = 4444
      }
    }
    task "eksi_app" {
      driver = "docker"
      env {
        TZ = "UTC-3"
      }
      // artifact {
      //   source = "/home/devlab/Desktop/Project_Merge/tar-files/eksi_scrape_img.tar"
      //   options {
      //     archive = false 
      //   }
      // }
      config {
        // load = "eksi_scrape_img.tar"
        image        = "python:3.9"
        command      = "python"
        args         = ["eksi_app.py"]
        work_dir     = "/app"
        network_mode = "bridge"
        privileged   = true

        // command = "sh"
        // args = ["-c", "sleep 6 && python /app/eksi_app.py && exit 0"]

        volumes = [
          "/host/path/config:/app/config",
          "/host/path/lib:/app/lib",
          "/host/path/log/userlog:/app/log",
        ]
      }
      resources {
        cpu    = 500
        memory = 1024
      }
    }
  }

  // group "youtube-scraping"{}

  // group "news-scraping"{ 
  //   network {
  //     mode = "bridge" 
  //     port "elastic" {
  //       static = 9200
  //     }
  //   }
  //   task "news-scraping" {
  //     driver = "docker"

  //     config {
  //       image = "scraping_img_rss"
  //       volumes = [
  //         "./config:/app/config",
  //         "./lib:/app/lib",
  //         "./log/userlog:/app/log",
  //       ]
  //     }
  //     env {TZ = "UTC-3"}
  //   }
  // }
}




  