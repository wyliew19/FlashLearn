# FlashLearn
"FlashLearn is a mobile application designed to facilitate efficient studying through the
use of customizable flashcards. The application will allow users to create, manage, and
study flashcards in a user-friendly interface. FlashLearn will support multiple study
modes, including spaced repetition, quizzes, and interactive games, to enhance
retention and engagement. The app will be developed for browser platforms, ensuring 
accessibility for a broad user base."

# Running the program
Utilizing the [devcontainer.json](.devcontainer/devcontainer.json) file, you can construct a Docker image for this project upon downloading the repository. Once the image is built, all dependencies and commands are ensured, and all you need to do is type `run` in the container's terminal

<sup>Note: the terminal may need to be restarted upon building the image for `run` to function</sup>

# UML Diagrams
## ER Diagram

```mermaid
erDiagram
    USER {
        INTEGER id PK
        TEXT email
        TEXT password
        TEXT name
    }
    SUPERSET {
        INTEGER id PK
        TEXT title
        INTEGER user_id FK
    }
    SUBSET {
        INTEGER id PK
        TEXT title
        INTEGER user_id FK
        INTEGER super_id FK
    }
    FLASHCARD {
        INTEGER id PK
        TEXT term
        TEXT body
        INTEGER user_id FK
        INTEGER set_id FK
        BOOLEAN studied
    }

    USER ||--o{ SUPERSET : "has"
    USER ||--o{ SUBSET : "has"
    USER ||--o{ FLASHCARD : "has"
    SUPERSET ||--o{ SUBSET : "contains"
    SUBSET ||--o{ FLASHCARD : "contains"
```

## Class Diagrams
### Users
```mermaid
classDiagram
    class User {
        +int id
        +str email
        +str name
    }

    class DatabaseManager {
        -DatabaseManager _instance
        +execute_query(query: str, params: list) list[tuple]
        +create_tables()
        +close_connection()
        +insert_into_table(table_name: str, **kwargs)
        +select_from_table(table_name: str, *columns, **kwargs) list[tuple]
        +update_table(table_name: str, new_vals: dict, **kwargs)
        +remove_from_table(table_name: str, **kwargs) list[tuple]
    }

    class UserHandler {
        -DatabaseManager _db
        +login(user:str, password: str) User
        +register(user: str, password: str, email: str) User
        +get_user(email: str) User
        +change_password(email: str, password: str, new_password: str) bool
    }

    UserHandler "0..*" -- "1" DatabaseManager : "uses"
    UserHandler -- User
    API -- User : "uses"
```

### Sets
```mermaid
classDiagram

    class AbstractSet {
        +int id
        +str title
        +str kind
    }

    class SuperSet {
        +list[Set] sets
    }

    class Set {
        +list[Card] cards
    }

    class Card {
        +int id
        +str term
        +str body
        +int user_id
        +int set_id
        +bool studied
    }

    class DatabaseManager {
        ...
    }

    class SetHandler {
        -DatabaseManager _db
        +create_set(name: str, user_id: int, super_id: int) Set
        +create_super_set(name: str, user_id: int) SuperSet
        -_populate_set(set_id: int) list[Card]
        -_populate_super_set(super_id: int) list[Set]
        -_get_unstudied_cards(set_id: int) list[Card]
        +get_set(set_id) Set
        +get_super_set(super_id: int) SuperSet
        +get_user_sets(user_id: int) list[AbstractSet]
        +get_subsets(super_id: int) list[Set]
        +edit_set(set_id: int, new_title: str) Set
        +edit_super_set(super_id: int, new_title: str) SuperSet
        +delete_set(set_id: int)
        +delete_super_set(super_id: int)
        +add_card_to_set(set_id: int, user_id: int, term: str, body: str) Card
        +get_card(card_id: int)
        +edit_card(card_id: int, new_term: str, new_body: str) Card
        +delete_card(card_id: int) bool
        +study_card(card_id: int) Card
        +get_next_unstudied_card(card_id: int, set_id: int) Card
    }

    DatabaseManager "1" -- "0..*" SetHandler : "uses"
    SuperSet "1" -- "0..*" Set : "contains"
    Set "1" -- "0..*" Card : "contains"
    AbstractSet <|-- SuperSet
    AbstractSet <|-- Set
    SetHandler -- Set
    SetHandler -- Card
    Card -- API : "uses"
    SuperSet -- API : "uses"
    Set -- API : "uses"
```

## Sequence Diagrams
### Database Interactions
```mermaid
sequenceDiagram
    participant User
    participant API
    participant Mediator
    participant Database

    User->>API: Send request
    API->>Mediator: Process request
    Mediator->>Database: Execute query
    Database-->>Mediator: Return data
    Mediator-->>API: Return response
    API-->>User: Return result
```
<sup>The "Mediator" participant is referencing the UserHandler and SetHandler objects</sup>

### User Interface Serving
```mermaid
sequenceDiagram
    participant User
    participant Browser
    participant API
    participant Jinja

    User->>Browser: Request page
    Browser->>API: Send HTTP request
    API->>Jinja: Render template
    Jinja-->>API: Return HTML
    API-->>Browser: Send HTML response
    Browser-->>User: Display page
```