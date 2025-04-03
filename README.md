# AlgoMeter AI Backend

This is the backend repository for AlgoMeter AI, a tool for analyzing code complexity and providing Big O insights (Time/Space Complexity) and Visualizations.

## Frontend Repository

For the frontend code, please visit: [AlgoMeter AI Frontend](https://github.com/raumildhandhukia/AlgoMeterAIFront)

## Description

AlgoMeter AI Backend is built with FastAPI and provides the following features:

- Code analysis for time and space complexity
- Rate limiting for API requests
- Integration with Gemini AI for code insights
- MongoDB integration for user data storage

## API Endpoints

- `/api/analyze`: POST request to analyze code snippets
- `/api/company-tags`: GET request to fetch company tags for LeetCode problems

### Company Tags Endpoint

The `/api/company-tags` endpoint allows you to fetch company tags and topic tags for LeetCode problems.

**Request:**

```
GET /api/company-tags?url=https%3A%2F%2Fleetcode.com%2Fproblems%2Ftwo-sum%2Fdescription%2F
```

**Response:**

```json
{
  "url": "https://leetcode.com/problems/two-sum/description/",
  "status": "success",
  "problem_id": "1",
  "title": "1. Two Sum",
  "title_slug": "two-sum",
  "difficulty": "Easy",
  "companies": ["Amazon", "Google", "Microsoft", "Apple", "Adobe"],
  "tags": ["Array", "Hash Table"]
}
```

## Technologies Used

- FastAPI
- Redis (for rate limiting)
- MongoDB
- Google Gemini AI
- Playwright (for browser automation)

## Setup

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Install Playwright browsers: `playwright install`
4. Copy `.env.example` to `.env` and fill in your credentials
5. For LeetCode authentication, you need to set the following environment variables:
   - `LEETCODE_CSRFTOKEN`: Your LeetCode CSRF token
   - `LEETCODE_SESSION`: Your LeetCode session token
   - `LEETCODE_CF_CLEARANCE`: Your Cloudflare clearance token

   You can get these tokens by logging into LeetCode in your browser and copying them from your browser's cookies.

## Debugging

This project includes several debugging configurations to help troubleshoot issues:

### VS Code Debug Configurations

1. **Python Debugger: app.py** - Debug the main application
2. **Install Playwright Browsers** - Install Playwright browsers required for web scraping
3. **Debug App** - Run the enhanced debug version of the app with additional logging
4. **Debug Playwright** - Run a standalone script to debug Playwright functionality
5. **Python Debugger: Current File** - Debug the currently open file

### Debugging the LeetCode API

If you encounter 403 Forbidden errors when accessing LeetCode:

1. Make sure your environment variables are set correctly in the `.env` file:
   - `LEETCODE_CSRFTOKEN`
   - `LEETCODE_SESSION`
   - `LEETCODE_CF_CLEARANCE`

2. Run the `Debug Playwright` configuration to test the Playwright browser automation with visual feedback

3. Run the `Debug App` configuration and access the `/debug/debug-company-tags` endpoint for enhanced logging

4. Check the generated log files and screenshots for troubleshooting information

## Deployment

This project is configured for deployment on Vercel. See the `vercel.json` file for deployment settings.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

[MIT License](LICENSE)
