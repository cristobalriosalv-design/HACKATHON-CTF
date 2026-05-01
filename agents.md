# Explanation of the project
This project is an EIATube clone that will be used as a challenge in a hackathon.
The participants in the hackathon will have to take the project and make it be able to sustain thousands of users concurrently in a stress test.

This challenge has the following dimensions:
- Optimize the code
- Make an adecuate infrastructure

# Your role in this project
Your role is to create the application that will be given to participants following the best coding practices like SOLID design principles, production grade repo structure, clear separation of concerns, etc. Basically, making a production grade application but with one small caveat, **small details must be poorly optimized by design**.

## Poor optimization explanation
Since the goal of the hackathon is the participants to optimize the code in such a way that it can sustain thousands of users, I want to deliberately leave poor optimization details that could hinder the participants unless they are not adressed.

Examples can be: Loading everything from the db eagerly, not using pagination, using poor search algorithms, etc.

That is why when developing I want you to purposefully add (or leave existing) unoptimized code.
