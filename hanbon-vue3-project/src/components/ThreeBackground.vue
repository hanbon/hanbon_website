<template>
    <div ref="threeContainer" class="three-container">
        <!-- 添加动态条纹层 -->
        <div class="stripe-container">
            <div class="stripe"></div>
            <div class="stripe"></div>
            <div class="stripe"></div>
            <div class="stripe"></div>
            <div class="stripe"></div>
        </div>
    </div>
</template>

<script>
import * as THREE from 'three';

export default {
    mounted() {
        this.initThree();
    },
    methods: {
        initThree() {
            const container = this.$refs.threeContainer;
            const scene = new THREE.Scene();
            const camera = new THREE.PerspectiveCamera(75, container.clientWidth / container.clientHeight, 0.1, 2000);
            const renderer = new THREE.WebGLRenderer({ 
                antialias: true,
                alpha: true 
            });
            renderer.setSize(container.clientWidth, container.clientHeight);
            renderer.setClearColor(0xf5f5f7, 1); // 浅灰背景色
            container.appendChild(renderer.domElement);

            // 创建网格背景
            const gridHelper = new THREE.GridHelper(2000, 50, 0xd1d1d6, 0xe5e5ea);
            gridHelper.position.y = -100;
            gridHelper.material.transparent = true;
            gridHelper.material.opacity = 0.3;
            scene.add(gridHelper);

            // 创建浮动粒子
            const particleGeometry = new THREE.BufferGeometry();
            const particleCount = 200;
            const positions = new Float32Array(particleCount * 3);
            const colors = new Float32Array(particleCount * 3);

            for (let i = 0; i < particleCount; i++) {
                // 位置
                positions[i * 3] = (Math.random() - 0.5) * 1000;
                positions[i * 3 + 1] = Math.random() * 500 - 100;
                positions[i * 3 + 2] = (Math.random() - 0.5) * 1000;

                // 颜色 - 使用浅蓝色系
                colors[i * 3] = 0.7 + Math.random() * 0.3;     // R
                colors[i * 3 + 1] = 0.8 + Math.random() * 0.2; // G
                colors[i * 3 + 2] = 1;                         // B
            }

            particleGeometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
            particleGeometry.setAttribute('color', new THREE.BufferAttribute(colors, 3));

            const particleMaterial = new THREE.PointsMaterial({
                size: 3,
                vertexColors: true,
                transparent: true,
                opacity: 0.6,
                blending: THREE.AdditiveBlending
            });

            const particles = new THREE.Points(particleGeometry, particleMaterial);
            scene.add(particles);

            // 添加连线效果
            const lineMaterial = new THREE.LineBasicMaterial({
                color: 0x0071e3,
                transparent: true,
                opacity: 0.2
            });

            const lineGeometry = new THREE.BufferGeometry();
            const linePositions = new Float32Array(particleCount * 6);
            lineGeometry.setAttribute('position', new THREE.BufferAttribute(linePositions, 3));
            const lines = new THREE.LineSegments(lineGeometry, lineMaterial);
            scene.add(lines);

            camera.position.z = 600;
            camera.position.y = 100;
            camera.lookAt(0, 0, 0);

            // 动画效果
            const animate = () => {
                requestAnimationFrame(animate);

                // 粒子动画
                const positions = particles.geometry.attributes.position.array;
                for (let i = 0; i < positions.length; i += 3) {
                    positions[i + 1] += Math.sin(Date.now() * 0.001 + i) * 0.1;
                }
                particles.geometry.attributes.position.needsUpdate = true;

                // 更新连线
                let lineIndex = 0;
                for (let i = 0; i < particleCount; i++) {
                    for (let j = i + 1; j < particleCount; j++) {
                        const dx = positions[i * 3] - positions[j * 3];
                        const dy = positions[i * 3 + 1] - positions[j * 3 + 1];
                        const dz = positions[i * 3 + 2] - positions[j * 3 + 2];
                        const dist = Math.sqrt(dx * dx + dy * dy + dz * dz);

                        if (dist < 150) {
                            linePositions[lineIndex++] = positions[i * 3];
                            linePositions[lineIndex++] = positions[i * 3 + 1];
                            linePositions[lineIndex++] = positions[i * 3 + 2];
                            linePositions[lineIndex++] = positions[j * 3];
                            linePositions[lineIndex++] = positions[j * 3 + 1];
                            linePositions[lineIndex++] = positions[j * 3 + 2];
                        }
                    }
                }
                lines.geometry.attributes.position.needsUpdate = true;

                // 网格动画
                gridHelper.rotation.y += 0.0005;
                
                renderer.render(scene, camera);
            };

            animate();

            // 处理窗口大小变化
            window.addEventListener('resize', () => {
                camera.aspect = container.clientWidth / container.clientHeight;
                camera.updateProjectionMatrix();
                renderer.setSize(container.clientWidth, container.clientHeight);
            });

            // 添加鼠标交互
            let mouseX = 0;
            let mouseY = 0;
            document.addEventListener('mousemove', (event) => {
                mouseX = (event.clientX - window.innerWidth / 2) * 0.05;
                mouseY = (event.clientY - window.innerHeight / 2) * 0.05;
            });

            // 相机动画
            const updateCamera = () => {
                camera.position.x += (mouseX - camera.position.x) * 0.05;
                camera.position.y += (-mouseY - camera.position.y) * 0.05;
                camera.lookAt(scene.position);
                requestAnimationFrame(updateCamera);
            };
            updateCamera();
        }
    }
}
</script>

<style scoped>
.three-container {
    width: 100%;
    height: 100vh;
    position: fixed;
    top: 0;
    left: 0;
    z-index: 0;
    background: linear-gradient(135deg, #f5f5f7 0%, #ffffff 100%);
    overflow: hidden;
}

/* 条纹容器 */
.stripe-container {
    position: absolute;
    width: 200%;
    height: 200%;
    top: -50%;
    left: -50%;
    z-index: 0;
    animation: rotate 20s linear infinite;
    pointer-events: none;
}

/* 条纹样式 */
.stripe {
    position: absolute;
    width: 200%;
    height: 2px;
    background: linear-gradient(90deg, 
        rgba(0, 113, 227, 0),
        rgba(0, 113, 227, 0.1),
        rgba(0, 113, 227, 0.2),
        rgba(0, 113, 227, 0.1),
        rgba(0, 113, 227, 0)
    );
    animation: moveStripe 8s linear infinite;
}

/* 设置不同条纹的位置和动画延迟 */
.stripe:nth-child(1) {
    top: 20%;
    animation-delay: 0s;
}

.stripe:nth-child(2) {
    top: 40%;
    animation-delay: -1s;
}

.stripe:nth-child(3) {
    top: 60%;
    animation-delay: -2s;
}

.stripe:nth-child(4) {
    top: 80%;
    animation-delay: -3s;
}

.stripe:nth-child(5) {
    top: 100%;
    animation-delay: -4s;
}

/* 条纹移动动画 */
@keyframes moveStripe {
    0% {
        transform: translateX(-50%) skewY(5deg);
    }
    100% {
        transform: translateX(0%) skewY(5deg);
    }
}

/* 容器旋转动画 */
@keyframes rotate {
    0% {
        transform: rotate(0deg);
    }
    100% {
        transform: rotate(360deg);
    }
}

/* 添加模糊和发光效果 */
.stripe::after {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    filter: blur(5px);
    background: inherit;
}

/* 移动端优化 */
@media (max-width: 768px) {
    .stripe {
        height: 1px;
    }
    
    .stripe-container {
        animation-duration: 30s;
    }
    
    @keyframes moveStripe {
        0% {
            transform: translateX(-50%) skewY(3deg);
        }
        100% {
            transform: translateX(0%) skewY(3deg);
        }
    }
}
</style>