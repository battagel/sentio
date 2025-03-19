<div align="center">
    <!-- TODO -->
    <!-- <img src="assets/logo.png" alt="logo" width="200" height="auto" /> -->
    <h1>Sentio - Anomaly detection</h1>
    <p>
        Anomaly detection for docker compose workloads using Prometheus, Grafana and Prophet.
    </p>
    <!-- Badges -->
    <p>
        <!-- <a href="https://github.com/battagel/sentio/graphs/contributors"> -->
        <!--   <img src="https://img.shields.io/github/contributors/battagel/sentio" alt="contributors" /> -->
        <!-- </a> -->
        <a href="https://github.com/battagel/sentio/network/members">
            <img src="https://img.shields.io/github/forks/battagel/sentio" alt="forks" />
        </a>
        <a href="https://github.com/battagel/sentio/stargazers">
            <img src="https://img.shields.io/github/stars/battagel/sentio" alt="stars" />
        </a>
        <a href="https://github.com/battagel/sentio/issues/">
            <img src="https://img.shields.io/github/issues/battagel/sentio" alt="open issues" />
        </a>
        <!-- TODO -->
        <!-- <a href="https://github.com/battagel/sentio/blob/master/LICENSE"> -->
        <!--   <img src="https://img.shields.io/github/license/battagel/sentio.svg" alt="license" /> -->
        <!-- </a> -->
    </p>
    <h4>
        <!--   <a href="https://github.com/battagel/sentio/">View Demo</a> -->
        <!-- <span> · </span> -->
        <!--   <a href="https://github.com/battagel/sentio">Documentation</a> -->
        <!-- <span> · </span> -->
        <a href="https://github.com/battagel/sentio/issues/">Report Bug</a>
        <span> · </span>
        <a href="https://github.com/battagel/sentio/issues/">Request Feature</a>
    </h4>
</div>

<br />

<!-- Table of Contents -->

# Table of Contents

- [About the Project](#about-the-project)
  - [Screenshots](#screenshots)
  - [Tech Stack](#tech-stack)
  - [Features](#features)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Developing Locally](#developing-locally)
  - [Running Tests](#running-tests)
  - [Linting](#linting)
- [Usage](#usage)
- [Contributing](#contributing)
- [FAQ](#faq)
- [License](#license)
- [Contact](#contact)
- [Acknowledgements](#acknowledgements)

<!-- About the Project -->

## About the Project

The Sentio container will take Prometheus' recorded metrics and predict the next
value (yhat) with an error range (yhat_upper, yhat_lower). This range can be
used to detect anomalous changes in the target metrics. We can then use an alert
algorithm to determine when to raise an alarm for the anomaly.

<!-- Screenshots -->

### Screenshots

<!-- <div align="center">  -->
<!--   <img src="https://placehold.co/600x400?text=Your+Screenshot+here" alt="screenshot" /> -->
<!-- </div> -->

<!-- TechStack -->

### Tech Stack

<details>
    <summary>ML</summary>
    <ul>
        <li><a href="https://facebook.github.io/prophet/">Prophet</a></li>
    </ul>
</details>
<details>
    <summary>Metrics</summary>
    <ul>
        <li><a href="https://prometheus.io/">Prometheus</a></li>
        <li><a href="https://grafana.com/">Grafana</a></li>
        <li><a href="https://www.influxdata.com/time-series-platform/telegraf/">Telegraf</a></li>
    </ul>
</details>

<!-- Features -->

### Features

- Detect anomalous activity on running docker compose workflows

<!-- Getting Started -->

## Getting Started

<!-- Prerequisites -->

### Prerequisites

This project requires docker and docker compose.

<!-- Installation -->

### Installation

Clone the repo.

<!-- Developing Locally -->

### Developing Locally

Bring the scenario up
``` sh
docker compose up --detach
```

Start the IO
``` sh
./run_io.sh
```

See the current load and the predicted load on Grafana. Navigate to dashboards to see some preproduced graphs
``` sh
http://localhost:3000
```


Bring the scenario down
``` sh
docker compose down
```

<!-- Running Tests -->

### Running Tests

N/A

<!-- Linting -->

### Linting

```bash
pylint .
```

<!-- Usage -->

## Usage

Head to `http://localhost:3000` to view the Grafana

<!-- Contributing -->

## Contributing

Contributions are always welcome!

See `contributing.md` for ways to get started.

<!-- FAQ -->

## FAQ

<!-- License -->

## License

TODO

<!-- Contact -->

## Contact

Matthew Battagel - matthew@battagel.me.uk - [GitHub](https://github.com/battagel)

<!-- Acknowledgments -->

## Acknowledgements

A big thanks to all of these resources:

- [Detecting Workload Anomalies with Prometheus and Machine Learning by Anthony Nocentino](https://www.youtube.com/watch?v=AleqE33JTgU)
