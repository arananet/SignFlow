/**
 * SignFlow 3D Avatar Renderer
 * 
 * Three.js-based renderer for sign language avatar animation
 */

import * as THREE from 'three';

export interface Frame {
  [bone: string]: number[]; // Quaternion [x, y, z, w]
}

export interface AnimationData {
  text: string;
  fps: number;
  frames: Frame[];
}

export class AvatarRenderer {
  private scene: THREE.Scene;
  private camera: THREE.PerspectiveCamera;
  private renderer: THREE.WebGLRenderer;
  private skeleton: THREE.Skeleton;
  private bones: Map<string, THREE.Bone>;
  private mixer: THREE.AnimationMixer;
  
  constructor(container: HTMLElement) {
    // Setup scene
    this.scene = new THREE.Scene();
    this.scene.background = new THREE.Color(0xf0f0f0);
    
    // Setup camera
    this.camera = new THREE.PerspectiveCamera(45, container.clientWidth / container.clientHeight, 0.1, 1000);
    this.camera.position.set(0, 1.5, 4);
    this.camera.lookAt(0, 1, 0);
    
    // Setup renderer
    this.renderer = new THREE.WebGLRenderer({ antialias: true });
    this.renderer.setSize(container.clientWidth, container.clientHeight);
    this.renderer.setPixelRatio(window.devicePixelRatio);
    this.renderer.shadowMap.enabled = true;
    container.appendChild(this.renderer.domElement);
    
    // Lighting
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
    this.scene.add(ambientLight);
    
    const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
    directionalLight.position.set(5, 10, 5);
    directionalLight.castShadow = true;
    this.scene.add(directionalLight);
    
    // Initialize skeleton and bones
    this.bones = new Map();
    this.skeleton = this.createSkeleton();
    this.mixer = new THREE.AnimationMixer(this.skeleton.bones[0]);
    
    // Create avatar mesh
    this.createAvatarMesh();
    
    // Start render loop
    this.animate();
  }
  
  private createSkeleton(): THREE.Skeleton {
    // Create bones for humanoid skeleton
    const bones: THREE.Bone[] = [];
    
    // Root and spine
    const root = new THREE.Bone();
    root.name = 'Root';
    root.position.set(0, 0, 0);
    bones.push(root);
    
    const spine = new THREE.Bone();
    spine.name = 'Spine';
    spine.position.set(0, 0.5, 0);
    root.add(spine);
    bones.push(spine);
    
    // Head
    const neck = new THREE.Bone();
    neck.name = 'Neck';
    neck.position.set(0, 0.3, 0);
    spine.add(neck);
    bones.push(neck);
    
    const head = new THREE.Bone();
    head.name = 'Head';
    head.position.set(0, 0.15, 0);
    neck.add(head);
    bones.push(head);
    
    // Left arm
    const leftShoulder = new THREE.Bone();
    leftShoulder.name = 'LeftShoulder';
    leftShoulder.position.set(-0.2, 0.2, 0);
    spine.add(leftShoulder);
    bones.push(leftShoulder);
    
    const leftArm = new THREE.Bone();
    leftArm.name = 'LeftArm';
    leftArm.position.set(-0.3, 0, 0);
    leftShoulder.add(leftArm);
    bones.push(leftArm);
    
    const leftForearm = new THREE.Bone();
    leftForearm.name = 'LeftForearm';
    leftForearm.position.set(-0.25, 0, 0);
    leftArm.add(leftForearm);
    bones.push(leftForearm);
    
    const leftHand = new THREE.Bone();
    leftHand.name = 'LeftHand';
    leftHand.position.set(-0.2, 0, 0);
    leftForearm.add(leftHand);
    bones.push(leftHand);
    
    // Right arm
    const rightShoulder = new THREE.Bone();
    rightShoulder.name = 'RightShoulder';
    rightShoulder.position.set(0.2, 0.2, 0);
    spine.add(rightShoulder);
    bones.push(rightShoulder);
    
    const rightArm = new THREE.Bone();
    rightArm.name = 'RightArm';
    rightArm.position.set(0.3, 0, 0);
    rightShoulder.add(rightArm);
    bones.push(rightArm);
    
    const rightForearm = new THREE.Bone();
    rightForearm.name = 'RightForearm';
    rightForearm.position.set(0.25, 0, 0);
    rightArm.add(rightForearm);
    bones.push(rightForearm);
    
    const rightHand = new THREE.Bone();
    rightHand.name = 'RightHand';
    rightHand.position.set(0.2, 0, 0);
    rightForearm.add(rightHand);
    bones.push(rightHand);
    
    // Store bones in map
    for (const bone of bones) {
      this.bones.set(bone.name, bone);
    }
    
    return new THREE.Skeleton(bones);
  }
  
  private createAvatarMesh() {
    // Create simple humanoid mesh
    const geometry = new THREE.CylinderGeometry(0.15, 0.2, 0.6, 16);
    const material = new THREE.MeshStandardMaterial({ color: 0x4a90d9 });
    const body = new THREE.Mesh(geometry, material);
    body.position.set(0, 1.1, 0);
    body.castShadow = true;
    this.scene.add(body);
    
    // Head
    const headGeometry = new THREE.SphereGeometry(0.15, 16, 16);
    const headMaterial = new THREE.MeshStandardMaterial({ color: 0xf5d0b0 });
    const head = new THREE.Mesh(headGeometry, headMaterial);
    head.position.set(0, 1.55, 0);
    head.castShadow = true;
    this.scene.add(head);
    
    // Arms (simplified cylinders)
    const armGeometry = new THREE.CylinderGeometry(0.05, 0.05, 0.6, 8);
    const armMaterial = new THREE.MeshStandardMaterial({ color: 0x4a90d9 });
    
    const leftArm = new THREE.Mesh(armGeometry, armMaterial);
    leftArm.position.set(-0.35, 1.2, 0);
    leftArm.rotation.z = 0.3;
    this.scene.add(leftArm);
    
    const rightArm = new THREE.Mesh(armGeometry, armMaterial);
    rightArm.position.set(0.35, 1.2, 0);
    rightArm.rotation.z = -0.3;
    this.scene.add(rightArm);
  }
  
  /**
   * Apply animation frames to avatar
   */
  public applyFrames(data: AnimationData): void {
    // For each frame, apply bone rotations
    // This is where STMC interpolation happens
    const duration = data.frames.length / data.fps;
    
    // Create animation clip
    const times: number[] = [];
    const tracks: THREE.KeyframeTrack[] = [];
    
    for (let i = 0; i < data.frames.length; i++) {
      times.push(i / data.fps);
      
      const frame = data.frames[i];
      for (const [boneName, quat] of Object.entries(frame)) {
        const bone = this.bones.get(boneName);
        if (bone) {
          // Create rotation track for this bone
          const track = new THREE.QuaternionKeyframeTrack(
            `${boneName}.quaternion`,
            [i / data.fps],
            quat
          );
          tracks.push(track);
        }
      }
    }
    
    const clip = new THREE.AnimationClip('sign', duration, tracks);
    this.mixer.clipAction(clip).play();
  }
  
  /**
   * Smooth motion using Gaussian filter
   */
  public smoothMotion(frames: Frame[]): Frame[] {
    // Apply Gaussian smoothing to bone positions
    const smoothed = [...frames];
    const kernel = [0.06, 0.12, 0.18, 0.24, 0.18, 0.12, 0.06]; // 7-point Gaussian
    
    for (const boneName of this.bones.keys()) {
      for (let i = 3; i < frames.length - 3; i++) {
        let sum = 0;
        for (let j = -3; j <= 3; j++) {
          const boneFrames = frames[i + j];
          if (boneFrames[boneName]) {
            sum += boneFrames[boneName][0] * kernel[j + 3];
          }
        }
        if (smoothed[i][boneName]) {
          smoothed[i][boneName][0] = sum;
        }
      }
    }
    
    return smoothed;
  }
  
  private animate() {
    requestAnimationFrame(() => this.animate());
    this.mixer.update(0.016); // ~60fps
    this.renderer.render(this.scene, this.camera);
  }
  
  public dispose() {
    this.renderer.dispose();
  }
}

/**
 * Main render function - initializes avatar
 */
export function renderAvatar(container: HTMLElement): AvatarRenderer {
  return new AvatarRenderer(container);
}

export default AvatarRenderer;
