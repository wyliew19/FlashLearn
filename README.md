# FlashLearn
"FlashLearn is a mobile application designed to facilitate efficient studying through the
use of customizable flashcards. The application will allow users to create, manage, and
study flashcards in a user-friendly interface. FlashLearn will support multiple study
modes, including spaced repetition, quizzes, and interactive games, to enhance
retention and engagement. The app will be developed for browser platforms, ensuring 
accessibility for a broad user base."
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
        TEXT name
        INTEGER user_id FK
    }
    SET {
        INTEGER id PK
        TEXT name
        INTEGER user_id FK
        INTEGER super_id FK
    }
    FLASHCARD {
        INTEGER id PK
        TEXT term
        TEXT body
        INTEGER user_id FK
        INTEGER set_id FK
    }

    USER ||--o{ SUPERSET : "has"
    USER ||--o{ SET : "has"
    USER ||--o{ FLASHCARD : "has"
    SUPERSET ||--o{ SET : "contains"
    SET ||--o{ FLASHCARD : "contains"
```
