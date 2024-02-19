job "Jira" {
  datacenters = ["dc2"]

  group "jira-software" {
    network {
      mode = "host"
      port "web" {
        to = 8080
      }
    }
    service {
      name = "jira-app"
      port = "http"
    }

    task "jira" {
      driver = "docker"
      config {
        image        = "atlassian/jira-software:8"
        network_mode = "host"
      }
      resources {
        cpu    = 500
        memory = 1024
      }
    }
  }
}
