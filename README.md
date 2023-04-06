<p align="center">
  <img src="https://user-images.githubusercontent.com/9355208/190904451-ac6f171b-26c6-4432-a04f-044974516da6.png" alt="Gameplan logo" height="50" />
  <p align="center">Delightful, open-source, work communication tool for remote teams</p>
</p>

<p align="center">
  <a href="https://dashboard.cypress.io/projects/y2q697/runs">
    <img alt="cypress" src="https://img.shields.io/endpoint?url=https://dashboard.cypress.io/badge/simple/y2q697/main&style=flat&logo=cypress">
  </a>
  <a href="https://github.com/dontmanage/gameplan/blob/main/LICENSE">
    <img alt="license" src="https://img.shields.io/badge/license-AGPLv3-blue">
  </a>
</p>

<img width="1402" alt="Screenshot 2022-09-18 at 9 16 08 PM" src="https://user-images.githubusercontent.com/9355208/190922102-daff8e9f-e34f-4129-a520-dcf834e92958.png">


<details>
  <summary>Show more screenshots</summary>

  <img width="1402" alt="Screenshot 2022-09-18 at 9 18 17 PM" src="https://user-images.githubusercontent.com/9355208/190922154-e5bdb690-57d3-4024-9143-9d009894b035.png">

  <img width="1402" alt="Screenshot 2022-09-18 at 9 18 47 PM" src="https://user-images.githubusercontent.com/9355208/190922161-61eb1cd7-a56a-4460-bc7f-d6c24d1c2df7.png">

  <img width="1402" alt="Screenshot 2022-09-18 at 11 47 06 PM" src="https://user-images.githubusercontent.com/9355208/190922333-fdad6271-2a77-4c7d-8d74-7c518d3052d6.png">


</details>

Gameplan is a work communication tool for teams who mostly work remote and prefer having meaningful discussions in an async format. We built it for ourselves because we were finding it difficult to keep track of so many conversations in our chat tool. Chat forces you to be online all the time and doesn't really have any concept of threaded discussions. Gameplan allows you to categorize your discussions around projects and teams. It also doubles up as your team's knowledge archive. You can surface important information and conclusions from your discussions into the readme's of your projects and teams.

## Features
- Organize discussions into projects which in turn are part of a team 🗄
- Surface important information for your project and team in the Readme 📝
- Simple layout that optimizes readability of discussions 🤓
- Customize your Team and Project with emojis 💅🏻
- People directory with each person's profile page 👨‍👩‍👧‍👦
- Set cover image, profile photo, short bio and a "About me" section 🦹🏼‍♀️
- Powerful search capabilities to find older discussions 🔍
- A common discussions feed that shows discussions from across projects and teams 📚
- Delightful user-experience in overall usage ✨

## Tech Stack

### Backend
Gameplan is built on [DontManage Framework](https://dontmanageframework.com) which is a batteries-included python web-framework.
These are some of the tools it's built on:
- [Python](https://www.python.org)
- [Redis](https://redis.io/)
- [MariaDB](https://mariadb.org/)
- [Socket.io](https://socket.io/)

### Frontend
The frontend of Gameplan is a VueJS SPA which uses a component library called [DontManage UI](https://github.com/dontmanage/dontmanage-ui).
These are some of the tools used on frontend:
- [VueJS](https://vuejs.org)
- [DontManage UI](https://github.com/dontmanage/dontmanage-ui)
- [TailwindCSS](https://tailwindcss.com)
- [HeadlessUI](https://headlessui.com)

## Local Setup
### Docker
You need Docker, docker-compose and git setup on your machine. Refer [Docker documentation](https://docs.docker.com/). After that, run the following commands:
```
git clone https://github.com/dontmanage/gameplan
cd gameplan/docker
docker-compose up
```

Wait for sometime until the setup script creates a site. After that you can
access `http://localhost:8000` in your browser and Gameplan's login screen
should show up.

Use the following credentials to log in:

- Username: `alex@example.com`
- Password: `123`

### DontManage Bench

Currently, this app depends on the `develop` branch of [dontmanage](https://github.com/dontmanage/dontmanage).

1. Setup dontmanage-bench by following [this guide](https://dontmanageframework.com/docs/v14/user/en/installation)
1. In the dontmanage-bench directory, run `bench start` and keep it running. Open a new terminal session and cd into `dontmanage-bench` directory.
1. Run the following commands:
    ```sh
    bench new-site gameplan.test
    bench get-app gameplan
    bench --site gameplan.test install-app gameplan
    bench --site gameplan.test add-to-hosts
    bench --site gameplan.test browse --user Administrator
    ```
 1. Now, open a new terminal session and cd into `dontmanage-bench/apps/gameplan`, and run the following commands:
    ```
    yarn
    yarn dev
    ```
 1. Now, you can access the site on vite dev server at `http://gameplan.test:8080`

## Deployment
Gameplan is an app built on top of DontManage Framework. So, you can follow any deployment guide for hosting a DontManage Framework based site.

### Managed Hosting
Gameplan can be deployed in a few clicks on [DontManage Cloud](https://dontmanagecloud.com/marketplace/apps/gameplan).

### Self hosting
If you want to self-host, you can follow official [DontManage Bench Installation](https://github.com/dontmanage/bench#installation) instructions.

## Discussions
If you have an idea that you think Gameplan should implement or you just want to hangout with other Gameplan users, you can join [Discussions](https://github.com/dontmanage/gameplan/discussions).

## Reporting Bugs
If you find any bugs, feel free to report them here on [GitHub Issues](https://github.com/dontmanage/gameplan/issues). Make sure you share enough information (app screenshots, browser console screenshots, stack traces, etc) for project maintainers to replicate your bug.

## License

AGPLv3
