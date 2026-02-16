/**
 * SignFlow Widget
 * 
 * Embeddable web component that renders sign language avatar
 * 
 * Usage:
 * <script src="signflow-widget.js"></script>
 * <signflow-widget api="https://api.signflow.com"></signflow-widget>
 */

import * as THREE from 'three';
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js';

export class SignFlowWidget {
  private container: HTMLElement | null = null;
  private scene: THREE.Scene | null = null;
  private camera: THREE.PerspectiveCamera | null = null;
  private renderer: THREE.WebGLRenderer | null = null;
  private bones: Map<string, THREE.Bone> = new Map();
  private apiUrl: string;
  private isExpanded: boolean = false;
  private currentAnimation: any = null;
  private animationFrame: number = 0;
  private fps: number = 30;

  constructor(apiUrl: string = 'https://api.signflow.com') {
    this.apiUrl = apiUrl;
    this.initUI();
    this.init3D();
    this.listenForTextSelection();
  }

  private initUI(): void {
    // Create bubble button
    const bubble = document.createElement('div');
    bubble.innerHTML = '🤟';
    bubble.style.cssText = `
      position: fixed;
      bottom: 20px;
      right: 20px;
      cursor: pointer;
      font-size: 30px;
      z-index: 9999;
      background: #fff;
      border-radius: 50%;
      box-shadow: 0 4px 12px rgba(0,0,0,0.15);
      padding: 10px;
      transition: transform 0.2s ease;
    `;
    
    bubble.onmouseenter = () => bubble.style.transform = 'scale(1.1)';
    bubble.onmouseleave = () => bubble.style.transform = 'scale(1)';
    
    // Create container
    this.container = document.createElement('div');
    this.container.style.cssText = `
      position: fixed;
      bottom: 80px;
      right: 20px;
      width: 300px;
      height: 400px;
      display: none;
      z-index: 9999;
      background: #fff;
      border-radius: 12px;
      overflow: hidden;
      box-shadow: 0 8px 32px rgba(0,0,0,0.2);
    `;
    
    bubble.onclick = () => {
      this.isExpanded = !this.isExpanded;
      this.container!.style.display = this.isExpanded ? 'block' : 'none';
    };
    
    document.body.appendChild(bubble);
    document.body.appendChild(this.container);
  }

  private init3D(): void {
    if (!this.container) return;
    
    this.scene = new THREE.Scene();
    this.camera = new THREE.PerspectiveCamera(45, 300 / 400, 0.1, 100);
    this.camera.position.set(0, 1.5, 3);
    this.camera.lookAt(0, 1, 0);
    
    this.renderer = new THREE.WebGLRenderer({ 
      alpha: true, 
      antialias: true 
    });
    this.renderer.setSize(300, 400);
    this.renderer.setPixelRatio(window.devicePixelRatio);
    this.container.appendChild(this.renderer.domElement);
    
    // Lighting
    const ambient = new THREE.AmbientLight(0xffffff, 0.8);
    this.scene.add(ambient);
    
    const directional = new THREE.DirectionalLight(0xffffff, 0.6);
    directional.position.set(5, 10, 7);
    this.scene.add(directional);
    
    // Load avatar model
    const loader = new GLTFLoader();
    loader.load(
      'https://your-cdn.com/avatar.glb',
      (gltf) => {
        const model = gltf.scene;
        this.scene!.add(model);
        
        // Map bones by name for JSON rotation application
        model.traverse((object) => {
          if ((object as any).isBone) {
            this.bones.set(object.name, object as THREE.Bone);
          }
        });
        
        console.log('Avatar loaded, bones:', Array.from(this.bones.keys()));
      },
      undefined,
      (error) => {
        console.error('Error loading avatar:', error);
        // Create fallback placeholder
        this.createPlaceholderAvatar();
      }
    );
    
    this.animate();
  }
  
  private createPlaceholderAvatar(): void {
    if (!this.scene) return;
    
    // Simple placeholder avatar
    const material = new THREE.MeshStandardMaterial({ color: 0x4a90d9 });
    
    // Body
    const body = new THREE.Mesh(
      new THREE.CylinderGeometry(0.15, 0.2, 0.6, 16),
      material
    );
    body.position.set(0, 1.1, 0);
    this.scene.add(body);
    
    // Head
    const head = new THREE.Mesh(
      new THREE.SphereGeometry(0.15, 16, 16),
      new THREE.MeshStandardMaterial({ color: 0xf5d0b0 })
    );
    head.position.set(0, 1.55, 0);
    this.scene.add(head);
  }

  private listenForTextSelection(): void {
    document.addEventListener('mouseup', async () => {
      const text = window.getSelection()?.toString().trim();
      
      if (text && text.length > 0 && this.isExpanded) {
        console.log('Selected text:', text);
        await this.translateAndPlay(text);
      }
    });
  }

  private async translateAndPlay(text: string): Promise<void> {
    try {
      const response = await fetch(`${this.apiUrl}/translate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text })
      });
      
      if (!response.ok) {
        throw new Error(`API error: ${response.status}`);
      }
      
      const data = await response.json();
      console.log('Translation received:', data);
      
      if (data.frames) {
        this.playAnimation(data.frames, data.fps || 30);
      }
    } catch (error) {
      console.error('Translation error:', error);
    }
  }

  private playAnimation(frames: any[], fps: number): void {
    this.currentAnimation = frames;
    this.animationFrame = 0;
    this.fps = fps;
  }

  private animate = (): void => {
    requestAnimationFrame(this.animate);
    
    // Play animation if available
    if (this.currentAnimation && this.currentAnimation.length > 0) {
      const frameData = this.currentAnimation[this.animationFrame];
      
      // Apply bone rotations from JSON
      for (const [boneName, quaternionArray] of Object.entries(frameData)) {
        const bone = this.bones.get(boneName);
        if (bone && Array.isArray(quaternionArray)) {
          bone.quaternion.fromArray(quaternionArray as number[]);
        }
      }
      
      // Advance frame
      this.animationFrame++;
      if (this.animationFrame >= this.currentAnimation.length) {
        this.animationFrame = 0; // Loop
      }
      
      // Throttle to FPS
      setTimeout(() => {}, 1000 / this.fps);
    }
    
    if (this.renderer && this.scene && this.camera) {
      this.renderer.render(this.scene, this.camera);
    }
  };
}

// Auto-initialize
document.addEventListener('DOMContentLoaded', () => {
  // Find widget container or create default
  const widgetElement = document.querySelector('signflow-widget');
  const apiUrl = widgetElement?.getAttribute('api') || 'https://api.signflow.com';
  
  new SignFlowWidget(apiUrl);
});

export default SignFlowWidget;
