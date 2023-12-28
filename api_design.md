# QUIZ APP API DESIGN

# Endpoints

## User Authentication and Management
**POST /users/register: Register a new user.**

**POST /users/login: Authenticate a user.**

**GET /users/{user_id}: Retrieve user information.**

**PUT /users/{user_id}: Update user profile.**

**DELETE /users/{user_id}: Delete user account.**

## Quiz Management
**POST /quizzes: Create a new quiz.**

**GET /quizzes/{quiz_id}: Retrieve details of a specific quiz.**

**PUT /quizzes/{quiz_id}: Update a quiz.**

**DELETE /quizzes/{quiz_id}: Delete a quiz.**

## Question Management
**POST /quizzes/{quiz_id}/questions: Add questions to a quiz.**

**GET /quizzes/{quiz_id}/questions: Get questions associated to a quiz.**

**GET /questions/{question_id}: Get a specific question.**

**PUT /questions/{question_id}: Update a specific question.**

**DELETE /questions/{question_id}: Delete a specific question.**

## Answer Options Management

**POST /questions/{question_id}/options: Add a new answer option to an existing question.**

**GET /questions/{question_id}/options: Get answer optiond associated to a question.**

**GET /options/{option_id}: Get an existing answer option.**

**PUT /options/{option_id}: Update an existing answer option.**

**DELETE /options/{option_id}: Delete an existing answer option.**

## Quiz Participation
**POST /quizzes/{quiz_id}/answers: Submit answers to a quiz.**

**POST /questions/{question_id}/answers: Submit answer to a question.**

**GET /quizzes/{quiz_id}/results: Get the results of a quiz attempt.**

**GET /quizzes/{quiz_id}/leaderboard: Show the top scores for a specific quiz.**

**GET /users/{user_id}/quizzes/attempts: Allow users to review their past quiz attempts.**

# Database Schemas

## Users Table
* Table Name: **users**
* Description: Stores information about the users.
* Columns:
    * id (Primary Key): Unique identifier for each user.
    * username (String, Unique): User's chosen username.
    * email (String, Unique): User's email address.
    * password_hash (String): Hashed password for security.
    * created_at (DateTime): Date and time of registration.

## Quizzes Table
* Table Name: **quizzes**
* Description: Stores basic information about quizzes.
* Columns:
    * id (Primary Key): Unique identifier for each quiz.
    * creator_id (Foreign Key to users): The user who created the quiz.
    * title (String): Title of the quiz.
    * description (String): Description or summary of the quiz.
    * created_at (DateTime): When the quiz was created.
    * updated_at (DateTime): Last update time.

## Questions Table
* Table Name: **questions**
* Description: Stores questions for each quiz.
* Columns:
    * id (Primary Key): Unique identifier for each question.
    * quiz_id (Foreign Key to quizzes): The quiz this question belongs to.
    * content (String): The actual question text.
    * type (String): The question type (multiple choice, true/false, open).
    * points (Integer): The question points (to compute quiz score).
    * created_at (DateTime): When the question was created.

## Answer Options Table
* Table Name: **answer_options**
* Description: Stores possible answers for each question (for multiple-choice questions).
* Columns:
    * id (Primary Key): Unique identifier for each option.
    * question_id (Foreign Key to questions): The question this option belongs to.
    * content (String): The text of the answer option.
    * is_correct (Bool): Flag to indicate if this is the correct option

## Quiz Attempts Table
* Table Name: **quiz_attempts**
* Description: Records each attempt a user makes on a quiz.
* Columns:
    * id (Primary Key): Unique identifier for each attempt.
    * quiz_id (Foreign Key to quizzes): The quiz attempted.
    * user_id (Foreign Key to users): The user who made the attempt.
    * score (Integer): The score achieved in the attempt.
    * attempted_at (DateTime): When the attempt was made.

## User Answers Table
* Table Name: **user_answers**
* Description: Stores the answers given by users in each attempt.
* Columns:
    * id (Primary Key): Unique identifier for each user answer.
    * attempt_id (Foreign Key to quiz_attempts): The attempt this answer is part of.
    * question_id (Foreign Key to questions): The question being answered.
    * chosen_option_id (Foreign Key to answer_options): The option chosen by the user.

## Relationships
* Users to Quizzes: One-to-Many (A user can create many quizzes).
* Quizzes to Questions: One-to-Many (A quiz contains many questions).
* Questions to Answer Options: One-to-Many (A question has multiple answer options).
* Users to Quiz Attempts: One-to-Many (A user can attempt many quizzes).
* Quizzes to Quiz Attempts: One-to-Many (A quiz can be attempted many times).
* Quiz Attempts to User Answers: One-to-Many (Each attempt can have multiple answers).
