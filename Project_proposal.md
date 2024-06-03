# Project Proposal

Design, develop and implement a Spotify Web API integration application that can connect a user's Spotify account and allow for personalized randomization and playlist creation.

## Project Basics

|            | Description|
| ---------- | ------- |
| Tech Stack |Python/Flask, PostgreSQL, Spotify Web API, HTML, CSS, JavaScript, WTForms|
| Type       |Website, possibly mobile app if time|
| Goal       |Create an oauth integrated application that will allow a user to upload their own Spotify profile and manipulate their libraries in order to improve randomization and specialization for playback.|
| Users      |The demographic should be anyone who routinely utilizes Spotify and wants to make randomized playlists that do not repeat the same few songs over and over again.|
| Data       |I will be utilizing the Spotify Web API for pulling data for individual users and sending data directly back to their accounts.|

# Project Breakdown (simplified)

*Please Note: Tasks are not in order of implementation, but grouped by the different components of the model view controller design pattern. This list is not inclusive and will change through the development process

| Task Name | Description | Difficulty                                                          |
| --------------------------- | -----------------------------| -------------------------|
| Frontend - Design | Integrate CSS/Bootstrap | moderate
| Frontend - Landing Page | App description and Login/Sign-up| moderate
| Frontend - Login Page | Navigation for different application capabilities and integration with user Spotify account | hard
|Frontend - WTForms Design | integrate standard design with Login and Signup forms | moderate
| Frontend - Favorites Randomization | Allow specific songs to be selected and added to randomization a set number of times | moderate
| Frontend - New Playlist | Allow specific songs to be selected and added to randomization a set number of times integrate with song search from Spotify and with existing favorites list | hard
| --------------------------- | -----------------------------| -------------------------|
|Backend - Set up database | Configure the environmental variables for PostgreSQL for development and set up database.
|Backend - WTForms Login and Sign-up Design and Integration | Design Login and Signup forms using WTForms | moderate
|Backend - WTForms Randomization Forms Design and Integration | Design Randomization forms using WTForms | moderate
|Backend - Integrate Spotify Web API using Flask | Create Flask pathways for API communication | moderate
|Backend - Routing | Create the routing for the entire application | moderate
| --------------------------- | -----------------------------| -------------------------|
|Model - User Model - User Authentication | Fullstack feature - ability to authenticate (login and sign up) as a user using Oath 2.0 standard.| moderate
|Model - User Model - Data Storage | Determine what information to store for the user to assure proper application communication and utilization | moderate
|Model - Song Model - Data Storage | Determine what information to store for the user to assure proper application communication and utilization | moderate
|Model - Song Model - Favorite / Multi-play | Add information to song model for song users wish to hear more often | moderate
|Model - API Model | Develop API model for single source of truth | moderate