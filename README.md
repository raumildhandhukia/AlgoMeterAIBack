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

## Technologies Used

- FastAPI
- Redis (for rate limiting)
- MongoDB
- Google Gemini AI

## Deployment

This project is configured for deployment on Vercel. See the `vercel.json` file for deployment settings.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

[MIT License](LICENSE)
