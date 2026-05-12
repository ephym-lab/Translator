# Language API Documentation

A REST API for a multilingual language platform supporting user authentication, translation, dataset management, and community-driven language contributions. Built with Python/FastAPI, served via Uvicorn.

**Base URL:** `http://127.0.0.1:8080/api/v1`

---

## Authentication

Most endpoints require a Bearer token in the `Authorization` header:

```
Authorization: Bearer <access_token>
```

Tokens are obtained from the Login endpoint. Access tokens are short-lived; use the refresh token to obtain new ones.

---

## Table of Contents

1. [Auth & Users](#1-auth--users)
2. [Languages](#2-languages)
3. [Tribes](#3-tribes)
4. [Subtribes](#4-subtribes)
5. [Categories](#5-categories)
6. [Datasets](#6-datasets)
7. [Responses](#7-responses)
8. [Votes](#8-votes)
9. [AI Generation](#9-ai-generation)
10. [Translation](#10-translation)
11. [Admin Endpoints](#11-admin-endpoints)

---

## 1. Auth & Users

### Register
**POST** `/users/register`

Creates a new user account. An OTP is sent to the provided email for verification.

**Request Body:**
```json
{
  "username": "Admin",
  "name": "Ephy Mucira",
  "email": "user@example.com",
  "password": "string",
  "gender": "male",
  "phone": "string",
  "avatar": "string",
  "languages": [
    "17e784d1-07e6-47ac-b42d-ee0341904e18",
    "171483bc-ce80-4738-8d89-d593aca569fd"
  ]
}
```

**Response** `201 Created`:
```json
{
  "message": "Registration successful. Check your email for the OTP.",
  "data": {
    "user_id": "405f1c14-2944-4066-ac7f-b3956c75b496",
    "email": "user@example.com",
    "username": "Admin",
    "name": "Ephy Mucira",
    "gender": "male",
    "phone": "string",
    "avatar": "string"
  }
}
```

---

### Verify OTP
**POST** `/users/verify-otp`

Verifies the OTP sent to the user's email after registration.

**Request Body:**
```json
{
  "email": "user@example.com",
  "code": "320924"
}
```

**Response** `200 OK`:
```json
{
  "message": "Email verified successfully."
}
```

---

### Login
**POST** `/users/login`

Authenticates the user and returns JWT access and refresh tokens.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "string"
}
```

**Response** `200 OK`:
```json
{
  "success": true,
  "message": "Logged in successfully.",
  "data": {
    "user": {
      "user_id": "405f1c14-2944-4066-ac7f-b3956c75b496",
      "email": "user@example.com",
      "username": "Admin",
      "role": "admin"
    },
    "tokens": {
      "access_token": "<jwt_token>",
      "refresh_token": "<jwt_token>",
      "token_type": "bearer"
    }
  },
  "status": 200
}
```

---

### Get My Profile
**GET** `/users/me`

🔒 Requires authentication.

Returns the authenticated user's profile including their associated languages.

**Response** `200 OK`:
```json
{
  "success": true,
  "message": "Profile retrieved successfully.",
  "data": {
    "id": "405f1c14-2944-4066-ac7f-b3956c75b496",
    "username": "Admin",
    "name": "Ephy Mucira",
    "email": "user@example.com",
    "gender": "male",
    "role": "admin",
    "phone": "string",
    "avatar": "string",
    "is_verified": true,
    "is_active": true,
    "languages": [
      { "id": "17e784d1-...", "name": "Kiswahili", "code": "ksw", "subtribe": null }
    ],
    "created_at": "2026-05-07T10:26:41.171211Z",
    "updated_at": "2026-05-07T10:28:05.754064Z"
  },
  "status": 200
}
```

---

### Update My Profile
**PATCH** `/users/me`

🔒 Requires authentication.

Updates the authenticated user's profile fields.

**Request Body** (all fields optional):
```json
{
  "username": "newUsername",
  "avatar": "https://example.com/avatar.png"
}
```

**Response** `200 OK`: Returns updated user profile (same shape as Get My Profile).

---

### Get User by ID
**GET** `/users/{user_id}`

🔒 Requires authentication.

Returns a specific user's profile.

**Path Parameter:** `user_id` — UUID of the target user.

**Response** `200 OK`: Same shape as Get My Profile.

---

### Get All Users
**GET** `/users/`

🔒 Requires authentication.

Returns a paginated list of all users.

**Response** `200 OK`:
```json
{
  "success": true,
  "message": "Users retrieved successfully.",
  "data": {
    "total": 2,
    "limit": 20,
    "offset": 0,
    "items": [ { ...user } ]
  },
  "status": 200
}
```

---

### Get My Languages
**GET** `/users/me/languages`

🔒 Requires authentication.

Returns the list of languages associated with the authenticated user.

**Response** `200 OK`:
```json
{
  "success": true,
  "message": "Languages retrieved successfully.",
  "data": [
    { "id": "17e784d1-...", "name": "Kiswahili", "code": "ksw", "subtribe": null }
  ]
}
```

---

### Add Language to My Profile
**POST** `/users/me/languages`

🔒 Requires authentication.

Associates a language with the authenticated user's profile.

**Request Body:**
```json
{
  "language_id": "6b5dcb89-86d0-49d4-8d49-63b06a3bee6a"
}
```

**Response** `201 Created`: Returns the updated list of user languages.

---

### Remove Language from My Profile
**DELETE** `/users/me/languages/{language_id}`

🔒 Requires authentication.

Removes a language from the authenticated user's profile.

**Path Parameter:** `language_id` — UUID of the language to remove.

**Response** `200 OK`:
```json
{
  "success": true,
  "message": "Language removed successfully.",
  "status": 200
}
```

---

## 2. Languages

### Get All Languages
**GET** `/languages/`

🔒 Requires authentication.

Returns a paginated list of all available languages.

**Response** `200 OK`:
```json
{
  "success": true,
  "message": "Languages retrieved successfully.",
  "data": {
    "total": 8,
    "limit": 20,
    "offset": 0,
    "items": [
      {
        "id": "17e784d1-07e6-47ac-b42d-ee0341904e18",
        "name": "Kiswahili",
        "code": "ksw",
        "subtribe_id": null,
        "created_at": "2026-05-06T11:55:04.426817Z"
      }
    ]
  },
  "status": 200
}
```

---

### Get Language by ID
**GET** `/languages/{language_id}`

🔒 Requires authentication.

Returns details of a single language.

**Path Parameter:** `language_id` — UUID of the language.

**Response** `200 OK`:
```json
{
  "success": true,
  "message": "Language fetched successfully.",
  "data": {
    "id": "17e784d1-07e6-47ac-b42d-ee0341904e18",
    "name": "Kiswahili",
    "code": "ksw",
    "subtribe_id": null,
    "created_at": "2026-05-06T11:55:04.426817Z"
  },
  "status": 200
}
```

---

## 3. Tribes

### Get All Tribes
**GET** `/tribes/`

🔒 Requires authentication.

Returns a paginated list of all tribes.

**Response** `200 OK`:
```json
{
  "message": "Tribes retrieved successfully.",
  "data": {
    "total": 4,
    "limit": 20,
    "offset": 0,
    "items": [
      {
        "id": "f79def35-5a54-4f83-ba51-fe3666722084",
        "name": "Kikuyu",
        "country": "Kenya",
        "country_code": "KE",
        "created_at": "2026-05-06T12:06:16.194391Z"
      }
    ]
  }
}
```

---

### Get Tribe by ID
**GET** `/tribes/{tribe_id}/`

🔒 Requires authentication.

Returns details of a single tribe.

**Path Parameter:** `tribe_id` — UUID of the tribe.

**Response** `200 OK`:
```json
{
  "message": "Tribe retrieved successfully.",
  "data": {
    "id": "f79def35-5a54-4f83-ba51-fe3666722084",
    "name": "Kikuyu",
    "country": "Kenya",
    "country_code": "KE",
    "created_at": "2026-05-06T12:06:16.194391Z"
  }
}
```

---

### Update Tribe
**PATCH** `/tribes/{tribe_id}/`

🔒 Requires authentication (Admin).

Updates a tribe's details.

**Path Parameter:** `tribe_id` — UUID of the tribe.

**Request Body** (all fields optional):
```json
{
  "country": "Uganda",
  "country_code": "UG"
}
```

**Response** `200 OK`: Returns the updated tribe object.

---

## 4. Subtribes

### Get All Subtribes
**GET** `/subtribes/`

🔒 Requires authentication.

Returns a paginated list of all subtribes.

**Response** `200 OK`:
```json
{
  "success": true,
  "message": "SubTribes retrieved successfully.",
  "data": {
    "total": 8,
    "limit": 20,
    "offset": 0,
    "items": [
      {
        "id": "5d22799e-fa59-4583-b6ca-1fc4bbad45f9",
        "name": "Nyeri",
        "tribe_id": "f79def35-5a54-4f83-ba51-fe3666722084",
        "created_at": "2026-05-06T12:28:14.545554Z"
      }
    ]
  },
  "status": 200
}
```

---

### Get Subtribe by ID
**GET** `/subtribes/{subtribe_id}`

🔒 Requires authentication.

Returns details of a single subtribe.

**Path Parameter:** `subtribe_id` — UUID of the subtribe.

**Response** `200 OK`:
```json
{
  "success": true,
  "message": "SubTribe retrieved successfully.",
  "data": {
    "id": "5d22799e-fa59-4583-b6ca-1fc4bbad45f9",
    "name": "Nyeri",
    "tribe_id": "f79def35-5a54-4f83-ba51-fe3666722084",
    "created_at": "2026-05-06T12:28:14.545554Z"
  },
  "status": 200
}
```

---

### Get Subtribes by Tribe
**GET** `/subtribes/by-tribe/{tribe_id}`

🔒 Requires authentication.

Returns all subtribes belonging to a specific tribe.

**Path Parameter:** `tribe_id` — UUID of the parent tribe.

**Response** `200 OK`: Returns an array of subtribe objects under `data`.

---

## 5. Categories

### Get All Categories
**GET** `/categories/`

🔒 Requires authentication.

Returns all contribution categories (e.g., voice, text).

**Response** `200 OK`:
```json
{
  "message": "Categories retrieved successfully.",
  "data": {
    "total": 2,
    "limit": 20,
    "offset": 0,
    "items": [
      {
        "id": "2fa3335a-7a6f-4383-8f9d-4d83ac680d3c",
        "name": "voice",
        "description": "Audio-based translation contributions",
        "created_at": "2026-05-06T12:54:26.569902Z"
      }
    ]
  }
}
```

---

### Get Category by ID
**GET** `/categories/{category_id}`

🔒 Requires authentication.

Returns details of a single category.

**Path Parameter:** `category_id` — UUID of the category.

**Response** `200 OK`:
```json
{
  "success": true,
  "message": "Category retrieved successfully.",
  "data": {
    "id": "2fa3335a-7a6f-4383-8f9d-4d83ac680d3c",
    "name": "voice",
    "description": "Audio-based translation contributions",
    "created_at": "2026-05-06T12:54:26.569902Z"
  },
  "status": 200
}
```

---

## 6. Datasets

### Get All Datasets
**GET** `/datasets/`

🔒 Requires authentication.

Returns a paginated list of all datasets.

**Response** `200 OK`:
```json
{
  "success": true,
  "message": "Datasets retrieved successfully.",
  "data": {
    "total": 32,
    "limit": 20,
    "offset": 0,
    "items": [
      {
        "id": "5bbe6bc9-fbb8-460f-8bd3-7257e718eedc",
        "original_text": "Hello",
        "level": "level_1",
        "response_percentage": 0,
        "is_clean": false,
        "allowed_categories": [ { ...category } ]
      }
    ]
  }
}
```

---

### Get Dataset by ID
**GET** `/datasets/{dataset_id}`

🔒 Requires authentication.

Returns a single dataset with its metadata.

**Path Parameter:** `dataset_id` — UUID of the dataset.

**Response** `200 OK`: Returns dataset object with `allowed_categories` array.

---

### Get AI-Generated Datasets
**GET** `/datasets/ai-generated`

🔒 Requires authentication.

Returns datasets that have AI-generated responses.

**Response** `200 OK`: Paginated list of dataset objects.

---

### Get Dataset Response Count
**GET** `/datasets/{dataset_id}/responses/count`

Returns the total and accepted response counts for a dataset.

**Path Parameter:** `dataset_id` — UUID of the dataset.

**Response** `200 OK`:
```json
{
  "success": true,
  "message": "Responses count retrieved successfully.",
  "data": {
    "total": 1,
    "accepted": 0
  },
  "status": 200
}
```

---

## 7. Responses

### Add Response
**POST** `/responses/`

🔒 Requires authentication.

Submits a user's translation response for a dataset entry.

**Request Body:**
```json
{
  "response_text": "string",
  "dataset_id": "3404763f-af80-4954-a67a-347b5c375582",
  "language_id": "6b5dcb89-86d0-49d4-8d49-63b06a3bee6a",
  "category_id": "2fa3335a-7a6f-4383-8f9d-4d83ac680d3c"
}
```

**Response** `201 Created`:
```json
{
  "success": true,
  "message": "Response submitted successfully.",
  "data": {
    "id": "c0ea2fcb-50d5-4d0c-9f45-330ab3042c77",
    "response_text": "string",
    "response_date": "2026-05-08T13:03:53.638743Z",
    "is_accepted": false,
    "user_id": "405f1c14-...",
    "dataset_id": "3404763f-...",
    "language_id": "6b5dcb89-...",
    "category_id": "2fa3335a-...",
    "created_at": "2026-05-08T13:03:53.638743Z"
  },
  "status": 201
}
```

---

### Get All Responses
**GET** `/responses/`

Returns a paginated list of all responses.

**Query Parameters (optional):**

| Parameter | Type | Description |
|---|---|---|
| `is_ai_generated` | boolean | Filter by whether the response was AI-generated |
| `vote_type` | string | Filter by vote type: `accept` or `reject` |

**Response** `200 OK`: Paginated list of response objects.

---

### Get Responses for a Dataset
**GET** `/responses/dataset/{dataset_id}`

🔒 Requires authentication.

Returns all responses for a specific dataset.

**Path Parameter:** `dataset_id` — UUID of the dataset.

**Query Parameters (optional):**

| Parameter | Type | Description |
|---|---|---|
| `vote_type` | string | Filter by `accept` or `reject` |
| `is_ai_generated` | boolean | Filter by AI-generated status |

**Response** `200 OK`: Paginated list of response objects.

---

### Update Response
**PATCH** `/responses/{response_id}`

🔒 Requires authentication.

Updates the text of an existing response.

**Path Parameter:** `response_id` — UUID of the response.

**Request Body:**
```json
{
  "response_text": "updated text"
}
```

**Response** `200 OK`: Returns the updated response object.

---

## 8. Votes

### Cast a Vote
**POST** `/votes/`

🔒 Requires authentication.

Casts a vote on a response (accept or reject).

**Request Body:**
```json
{
  "vote": "accept",
  "response_id": "c0ea2fcb-50d5-4d0c-9f45-330ab3042c77"
}
```

**Response** `201 Created`:
```json
{
  "success": true,
  "message": "Vote cast successfully.",
  "data": {
    "id": "3dc7f7c9-a4f0-41a8-bd6b-13c372942f5a",
    "vote": "accept",
    "user_id": "405f1c14-...",
    "response_id": "c0ea2fcb-...",
    "created_at": "2026-05-08T13:11:33.711773Z"
  },
  "status": 201
}
```

---

### Get Votes for a Response
**GET** `/votes/response/{response_id}`

Returns all votes cast on a specific response.

**Path Parameter:** `response_id` — UUID of the response.

**Response** `200 OK`:
```json
{
  "total": 1,
  "limit": 20,
  "offset": 0,
  "items": [
    {
      "id": "c3bdf82b-...",
      "vote": "accept",
      "user_id": "650f2f5c-...",
      "response_id": "d232f053-...",
      "created_at": "2026-05-06T16:08:22.271122Z"
    }
  ]
}
```

---

### Get Vote Count for a Response
**GET** `/votes/response/{response_id}/count`

Returns the total, accepted, and rejected vote counts for a response.

**Path Parameter:** `response_id` — UUID of the response.

**Response** `200 OK`:
```json
{
  "success": true,
  "message": "Votes count retrieved successfully.",
  "data": {
    "total": 0,
    "accepted": 0,
    "rejected": 0
  },
  "status": 200
}
```

---

## 9. AI Generation

### Generate Dataset
**POST** `/ai/generate-dataset`

🔒 Requires authentication (Admin).

Triggers AI-based generation of dataset entries for a given language and level.

**Request Body:**
```json
{
  "language_id": "8a139c67-9b15-4ae9-b2b9-d3447ba95534",
  "level": "level_1"
}
```

**Extended Request Body** (with optional parameters):
```json
{
  "language_id": "8a139c67-9b15-4ae9-b2b9-d3447ba95534",
  "level": "level_1",
  "category_ids": ["834204ba-a8f0-4313-9172-a8657688bfeb"],
  "target_languages": [
    "6b5dcb89-86d0-49d4-8d49-63b06a3bee6a",
    "171483bc-ce80-4738-8d89-d593aca569fd"
  ],
  "generation_count": 5
}
```

**Request Fields:**

| Field | Type | Required | Description |
|---|---|---|---|
| `language_id` | UUID | Yes | Source language for the dataset |
| `level` | string | Yes | Difficulty level (e.g. `level_1`) |
| `category_ids` | UUID[] | No | Categories to associate with generated datasets |
| `target_languages` | UUID[] | No | Languages to generate AI responses for |
| `generation_count` | integer | No | Number of datasets to generate (default: 20) |

**Response** `201 Created`:
```json
{
  "success": true,
  "message": "5 dataset(s) generated successfully.",
  "data": [ { ...dataset } ]
}
```

---

## 10. Translation

### Normal Translate
**POST** `/translate/normal-translate`

🔒 Requires authentication.

Performs a synchronous text translation between two languages.

**Request Body:**
```json
{
  "text": "sasa",
  "source_lang": "swahili",
  "target_lang": "english"
}
```

**Response** `200 OK`:
```json
{
  "message": "Translation successful",
  "data": {
    "original": "sasa",
    "translated": "now",
    "source_lang": "swahili",
    "target_lang": "english"
  }
}
```

---

### Async Translate
**POST** `/translate/async-translate`

🔒 Requires authentication.

Performs an asynchronous text translation. Suitable for longer or queued translation workloads.

**Request Body:**
```json
{
  "text": "uko vipi",
  "source_lang": "swahili",
  "target_lang": "english"
}
```

**Response** `200 OK`:
```json
{
  "message": "Translation successful",
  "data": {
    "original": "uko vipi",
    "translated": "How are you?",
    "source_lang": "swahili",
    "target_lang": "english"
  }
}
```

---

## 11. Admin Endpoints

These endpoints are restricted to users with the `admin` role.

### Create Language
**POST** `/languages/`

**Request Body:**
```json
{
  "name": "Kikuyu",
  "code": "kik"
}
```

**Response** `201 Created`: Returns the created language object.

---

### Update Language
**PATCH** `/languages/{language_id}`

**Path Parameter:** `language_id` — UUID of the language.

**Request Body:**
```json
{
  "name": "string",
  "code": "string"
}
```

**Response** `200 OK`: Returns the updated language object.

---

### Delete Language
**DELETE** `/languages/{language_id}`

**Path Parameter:** `language_id` — UUID of the language.

**Response** `200 OK`:
```json
{
  "success": true,
  "message": "Language deleted successfully.",
  "status": 200
}
```

---

### Create Tribe
**POST** `/tribes/`

**Request Body:**
```json
{
  "name": "Somali",
  "country": "Kenya",
  "country_code": "KE"
}
```

**Response** `201 Created`: Returns the created tribe object.

---

### Create Subtribe
**POST** `/subtribes/`

**Request Body:**
```json
{
  "name": "Ndia",
  "tribe_id": "f79def35-5a54-4f83-ba51-fe3666722084",
  "language_id": "171483bc-ce80-4738-8d89-d593aca569fd"
}
```

**Response** `201 Created`: Returns the created subtribe object.

---

### Update Subtribe
**PATCH** `/subtribes/{subtribe_id}`

**Path Parameter:** `subtribe_id` — UUID of the subtribe.

**Request Body:**
```json
{
  "name": "NewName"
}
```

**Response** `200 OK`: Returns the updated subtribe object.

---

### Create Category
**POST** `/categories/`

**Request Body:**
```json
{
  "name": "machine",
  "description": "Machine-based translation contributions"
}
```

**Response** `201 Created`: Returns the created category object.

---

### Update Category
**PATCH** `/categories/{category_id}`

**Path Parameter:** `category_id` — UUID of the category.

**Request Body:**
```json
{
  "description": "Updated description"
}
```

**Response** `200 OK`: Returns the updated category object.

---

### Create Dataset
**POST** `/datasets/`

**Request Body:**
```json
{
  "original_text": "string",
  "level": "level_1",
  "category_ids": ["2fa3335a-7a6f-4383-8f9d-4d83ac680d3c"],
  "language_id": "17e784d1-07e6-47ac-b42d-ee0341904e18"
}
```

**Response** `201 Created`: Returns the created dataset object.

---

### Update Dataset
**PATCH** `/datasets/{dataset_id}`

**Path Parameter:** `dataset_id` — UUID of the dataset.

**Request Body:**
```json
{
  "original_text": "updated text"
}
```

**Response** `200 OK`: Returns the updated dataset object.

---

## Error Responses

All error responses follow this format:

```json
{
  "detail": "Error message here"
}
```

| Status Code | Meaning |
|---|---|
| `400` | Bad Request — invalid input |
| `401` | Unauthorized — missing or invalid token |
| `403` | Forbidden — insufficient permissions |
| `404` | Not Found — resource does not exist |
| `422` | Unprocessable Entity — validation error |
| `500` | Internal Server Error |

---

## Pagination

All list endpoints return paginated responses with the following structure:

```json
{
  "total": 32,
  "limit": 20,
  "offset": 0,
  "items": [ ...results ]
}
```

Use `limit` and `offset` as query parameters to paginate through results.