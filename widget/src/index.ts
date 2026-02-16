/**
 * SignFlow Widget - Entry Point
 * 
 * Embeddable web component that renders sign language avatar
 * 
 * Usage:
 * <script src="signflow-widget.js"></script>
 * <signflow-widget api="https://api.signflow.com"></signflow-widget>
 */

import { renderAvatar } from './engine/renderer';

export interface SignFlowConfig {
  apiUrl: string;
  position?: 'bottom-right' | 'bottom-left';
  theme?: 'light' | 'dark';
}

export class SignFlowWidget extends HTMLElement {
  private shadow: ShadowRoot;
  private config: SignFlowConfig;
  private isExpanded: boolean = false;

  constructor() {
    super();
    this.shadow = this.attachShadow({ mode: 'open' });
    this.config = {
      apiUrl: this.getAttribute('api') || 'https://api.signflow.com',
      position: (this.getAttribute('position') as any) || 'bottom-right',
      theme: (this.getAttribute('theme') as any) || 'dark'
    };
  }

  connectedCallback() {
    this.render();
    this.setupEventListeners();
  }

  private render() {
    this.shadow.innerHTML = `
      <style>
        :host {
          position: fixed;
          ${this.config.position}: 20px;
          z-index: 999999;
          font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        }
        
        .widget-toggle {
          width: 60px;
          height: 60px;
          border-radius: 50%;
          background: ${this.config.theme === 'dark' ? '#1a1a2e' : '#fff'};
          border: 2px solid #0066cc;
          cursor: pointer;
          display: flex;
          align-items: center;
          justify-content: center;
          box-shadow: 0 4px 20px rgba(0,0,0,0.3);
          transition: transform 0.3s ease;
        }
        
        .widget-toggle:hover {
          transform: scale(1.1);
        }
        
        .widget-panel {
          position: absolute;
          bottom: 70px;
          right: 0;
          width: 320px;
          height: 400px;
          background: ${this.config.theme === 'dark' ? '#1a1a2e' : '#fff'};
          border-radius: 16px;
          box-shadow: 0 8px 32px rgba(0,0,0,0.3);
          overflow: hidden;
          display: ${ 'block' :this.isExpanded ? 'none'};
        }
        
        .avatar-container {
          width: 100%;
          height: 280px;
          background: ${this.config.theme === 'dark' ? '#0f0f1a' : '#f0f0f0'};
        }
        
        .input-area {
          padding: 12px;
          display: flex;
          gap: 8px;
        }
        
        .input-area input {
          flex: 1;
          padding: 10px 14px;
          border: 1px solid #ddd;
          border-radius: 8px;
          font-size: 14px;
        }
        
        .input-area button {
          padding: 10px 16px;
          background: #0066cc;
          color: white;
          border: none;
          border-radius: 8px;
          cursor: pointer;
          font-weight: 600;
        }
        
        .status {
          padding: 8px 12px;
          font-size: 12px;
          color: #666;
          text-align: center;
        }
      </style>
      
      <div class="widget-panel">
        <div class="avatar-container" id="avatar"></div>
        <div class="input-area">
          <input type="text" id="text-input" placeholder="Type text to sign..." />
          <button id="sign-btn">Sign</button>
        </div>
        <div class="status" id="status">Ready</div>
      </div>
      
      <div class="widget-toggle" id="toggle">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#0066cc" stroke-width="2">
          <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2z"/>
          <path d="M8 12l2 2 4-4"/>
        </svg>
      </div>
    `;
  }

  private setupEventListeners() {
    const toggle = this.shadow.getElementById('toggle');
    const input = this.shadow.getElementById('text-input') as HTMLInputElement;
    const btn = this.shadow.getElementById('sign-btn');
    const status = this.shadow.getElementById('status');

    toggle?.addEventListener('click', () => {
      this.isExpanded = !this.isExpanded;
      this.render();
    });

    btn?.addEventListener('click', async () => {
      const text = input?.value;
      if (!text) return;
      
      status.textContent = 'Translating...';
      
      try {
        const response = await fetch(`${this.config.apiUrl}/translate`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ text })
        });
        
        const data = await response.json();
        
        if (data.frames) {
          status.textContent = 'Rendering...';
          // Render would happen here via Three.js
          status.textContent = 'Playing...';
        }
      } catch (e) {
        status.textContent = 'Error: ' + (e as Error).message;
      }
    });
  }
}

// Register custom element
customElements.define('signflow-widget', SignFlowWidget);

export default SignFlowWidget;
