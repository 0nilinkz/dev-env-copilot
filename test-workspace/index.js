const express = require('express');
const axios = require('axios');

const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(express.json());

// Routes
app.get('/', (req, res) => {
    res.json({
        message: 'Test API for Dev Environment Copilot',
        version: '1.0.0',
        environment: process.env.NODE_ENV || 'development'
    });
});

app.get('/health', (req, res) => {
    res.status(200).json({ status: 'OK', timestamp: new Date().toISOString() });
});

// Potential security issue: sensitive data in logs
app.post('/login', (req, res) => {
    const { username, password } = req.body;
    
    // BAD: Logging sensitive information
    console.log(`Login attempt: ${username}:${password}`);
    
    // Simulate authentication
    if (username === 'admin' && password === 'password123') {
        res.json({ success: true, token: 'fake-jwt-token' });
    } else {
        res.status(401).json({ success: false, message: 'Invalid credentials' });
    }
});

app.listen(PORT, () => {
    console.log(`Server running on port ${PORT}`);
});
