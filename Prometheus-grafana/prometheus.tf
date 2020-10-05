terraform {
  backend "remote" {
    organization = "devopsproject"

    workspaces {
      name = "DO-project-Insight"
    }
  }
}


module "helm-release" {
  source         = "edalferes/release/helm"
  version        = "1.4.0-release.216997"
  config_context = "minikube"

  release = {
    prometheus-operator = {
      repository_name     = "stable"
      repository_url      = "https://kubernetes-charts.storage.googleapis.com"
      repository_username = null
      repository_password = null
      version             = "8.12.12"
      chart               = "prometheus-operator"
      force_update        = true
      wait                = false
      recreate_pods       = false
      values              = null
      set_strings         = null
      set                 = null
    }

  }
}

/*
resource "kubernetes_config_map" "config-map-aws-auth" {
  metadata {
    name      = "aws-auth"
    namespace = "kube-system"
  }

  data = {
    "my_config_file.yml" = "${file("${path.module}/config-map-aws-auth_test-eks-dev.yaml")}"
  }

}
*/
