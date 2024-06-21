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
        string email PK
        string password
        string name
    }
    FLASHCARD {
        int id PK
        string text
        string image_url
        int user_id FK
        int set_id FK
    }
    SET {
        int id PK
        string name
        int user_id FK
    }
    STUDY_SESSION {
        int id PK
        datetime start_time
        datetime end_time
        int user_id FK
    }
    SESSION_FLASHCARD {
        int session_id FK
        int flashcard_id FK
        boolean correct
    }
    SHARED_SET {
        int set_id FK
        string receiver_email
    }

    USER ||--o{ FLASHCARD : "creates/owns"
    USER ||--o{ SET : "creates/owns"
    SET ||--o{ FLASHCARD : "contains"
    USER ||--o{ STUDY_SESSION : "has"
    STUDY_SESSION ||--o{ SESSION_FLASHCARD : "includes"
    FLASHCARD ||--o{ SESSION_FLASHCARD : "reviewed in"
    SET ||--o{ SHARED_SET : "shared"
```
