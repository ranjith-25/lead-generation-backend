importScripts('https://www.gstatic.com/firebasejs/10.8.0/firebase-app-compat.js');
importScripts('https://www.gstatic.com/firebasejs/10.8.0/firebase-messaging-compat.js');

firebase.initializeApp({
    apiKey: "AIzaSyBRU6dtl4WP5Bc7cebN9-QNwT7bzxcKU4o",
    authDomain: "ai-lead-generation-cbc76.firebaseapp.com",
    projectId: "ai-lead-generation-cbc76",
    storageBucket: "ai-lead-generation-cbc76.firebasestorage.app",
    messagingSenderId: "973282866",
    appId: "1:973282866:web:c52acaa8851a42aba2262b",
    measurementId: "G-L6C74HKSEC"
});

const messaging = firebase.messaging();

messaging.onBackgroundMessage((payload) => {
    console.log('Background push received:', payload);
    self.registration.showNotification(payload.notification.title, {
        body: payload.notification.body,
        icon: payload.notification.icon || ''
    });
});