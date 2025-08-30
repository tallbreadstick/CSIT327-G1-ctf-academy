# CTF Academy

A web platform for education in higher-level abstractions of cybersecurity and pentesting tools, techniques, and methodologies.

## About

CTF Academy is a web-based platform designed to train users by giving them experience dealing with abstract cybersecurity and pentesting concepts. The platform takes a leetcode-style approach, providing an open problem set with various capture-the-flag style challenges. Each challenge introduces different key cybersecurity concepts from the basics to intermediate, including endpoints, exposed surfaces, privileges, and encryption.

Each challenge contains a graph of nodes which represents a network of host machines, mimicing real world network topologies and security layers. Users must use a set of given tools to inspect, analyze, and understand system architectures with the objective of finding exploits that lead them to capturing the flag. Tools provided to users will include terminals, scripts, and webviews.

Challenges range from various difficulties including easy, medium, and hard problems. Higher difficulty challenges completed award higher points to a user's general ranking on the leaderboards. Users' challenge histories, attempts, and submissions are also recorded. CTF Academy also fosters continuous support through streaks, encouraging users to maintain daily challenge streaks to gain score bonuses.

## Backend Internals

This section dictates specifications for backend internals with respect to different individual features.

### Challenges

Each challenge's data, details, and specifications are stored as static resources in the application's backend. When a user attempts a challenge, a docker container is created according to the challenge's specifications. This wills serve as the sandbox or the challenge play area. All interactions with terminal tools, scripts, and webviews as well as mutable interactions with nodes occur within the user's open docker container for the challenge. Challenge state is stored on the cloud in the application's backend database. Returning to a challenge in progress restores the saved state of the challenge.

### Ranking and Streaks

As users complete challenges, points are awarded to their accounts. Every consecutive day in which a challenge is solved awards a growing score multiplier. Breaking a steak resets the score multiplier. Scores and streaks are also stored persistently in the application's backend database.