/**
 * Application Entry Point
 */
import React from 'react';
import ReactDOM from 'react-dom/client';
import { ConfigProvider } from 'antd';
import zhCN from 'antd/locale/zh_CN';
import App from './App';
import './index.css';

// Initialize database and check auth on startup
async function initApp() {
  try {
    const { initDB } = await import('./db');
    await initDB();

    // Run migrations
    const { runMigrations } = await import('./db');
    await runMigrations();
  } catch (error) {
    console.error('Failed to initialize database:', error);
  }
}

// Initialize and render
initApp().then(() => {
  ReactDOM.createRoot(document.getElementById('root')!).render(
    <React.StrictMode>
      <ConfigProvider locale={zhCN}>
        <App />
      </ConfigProvider>
    </React.StrictMode>
  );
});
