const fs = require('fs');
const { createCanvas } = require('canvas');

// Create a 128x128 canvas
const canvas = createCanvas(128, 128);
const ctx = canvas.getContext('2d');

// Background
ctx.fillStyle = '#007ACC';
ctx.fillRect(0, 0, 128, 128);

// Terminal window
ctx.fillStyle = '#1e1e1e';
ctx.fillRect(20, 35, 88, 58);

// Border
ctx.strokeStyle = '#ffffff';
ctx.lineWidth = 1;
ctx.strokeRect(20, 35, 88, 58);

// Terminal prompt
ctx.fillStyle = '#00ff00';
ctx.fillRect(28, 46, 12, 2);

ctx.fillStyle = '#ffffff';
ctx.fillRect(28, 56, 32, 1);
ctx.fillRect(28, 66, 17, 1);
ctx.fillRect(28, 76, 42, 1);

// Copilot dots
ctx.fillStyle = '#ff6b6b';
ctx.beginPath();
ctx.arc(85, 52, 8, 0, 2 * Math.PI);
ctx.fill();

ctx.fillStyle = '#4ecdc4';
ctx.beginPath();
ctx.arc(95, 65, 6, 0, 2 * Math.PI);
ctx.fill();

ctx.fillStyle = '#45b7d1';
ctx.beginPath();
ctx.arc(85, 78, 5, 0, 2 * Math.PI);
ctx.fill();

// Save as PNG
const buffer = canvas.toBuffer('image/png');
fs.writeFileSync('icon.png', buffer);

console.log('Icon created successfully!');
