import streamlit as str
import streamlit.components.v1 as components

# 페이지 설정
str.set_page_config(page_title="Streamlit QWER Rhythm Game", layout="centered")

str.title("🎵 QWER 리듬 게임")
str.subheader("스트림릿에서 즐기는 실시간 리듬 게임")

# 게임 설명
str.markdown("""
* **조작 방법**: `Q`, `W`, `E`, `R` 키를 타이밍에 맞춰 누르세요!
* 노트가 하단의 **판정선(붉은색 선)**에 닿았을 때 정확히 누르면 득점합니다.
* **잘못된 키를 누르거나, 타이밍이 맞지 않으면 점수가 감점(-30점)**되니 주의하세요!
* 아래 게임 화면을 **한 번 클릭**하여 포커스를 준 후 플레이해주세요.
""")

# JavaScript + HTML5 Canvas 기반의 게임 코드
game_html = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {
            background-color: #1e1e1e;
            color: white;
            font-family: 'Arial', sans-serif;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            margin: 0;
            overflow: hidden;
        }
        canvas {
            border: 4px solid #00D2FF;
            background-color: #111;
            box-shadow: 0px 0px 20px rgba(0,0,0,0.5);
        }
        #scoreBoard {
            font-size: 24px;
            margin-bottom: 10px;
            font-weight: bold;
        }
        #comboBoard {
            font-size: 20px;
            color: #FFD700;
            margin-bottom: 5px;
            height: 24px;
        }
    </style>
</head>
<body>

<div id="scoreBoard">SCORE: <span id="score">0</span></div>
<div id="comboBoard"><span id="combo"></span></div>
<canvas id="gameCanvas" width="400" height="500"></canvas>

<script>
const canvas = document.getElementById("gameCanvas");
const ctx = canvas.getContext("2d");

// QWER 게임 설정 변경
const lanes = ['Q', 'W', 'E', 'R'];
const laneX = { 'Q': 50, 'W': 150, 'E': 250, 'R': 350 };
const laneWidth = 100;
const judgmentLineY = 430; // 판정선 위치
const noteSpeed = 5;       // 노트 하강 속도
const tolerance = 30;      // 판정 범위 (픽셀)

let score = 0;
let combo = 0;
let notes = [];
let keyStates = { 'Q': false, 'W': false, 'E': false, 'R': false };
let judgmentTexts = []; // 판정 텍스트 이펙트 저장

// 노트 생성 타이머 (주기적으로 노트 생성)
setInterval(() => {
    const randomLane = lanes[Math.floor(Math.random() * lanes.length)];
    notes.push({
        lane: randomLane,
        y: 0,
        color: getRandomColor(randomLane)
    });
}, 600);

// 레인별 노트 색상 지정
function getRandomColor(lane) {
    if (lane === 'Q') return '#FF5733'; // 주황
    if (lane === 'W') return '#33FF57'; // 연두
    if (lane === 'E') return '#3357FF'; // 파랑
    if (lane === 'R') return '#F3FF33'; // 노랑
}

// 키보드 입력 이벤트
window.addEventListener('keydown', (e) => {
    let key = e.key.toUpperCase();
    
    // 1. QWER 중 하나를 눌렀을 때
    if (lanes.includes(key)) {
        if (!keyStates[key]) {
            keyStates[key] = true;
            checkJudgment(key);
        }
    } else {
        // 2. QWER 외의 엉뚱한 키를 눌렀을 때 (감점 처리 및 아무 레인에나 MISS 이펙트)
        triggerWrongKey();
    }
});

window.addEventListener('keyup', (e) => {
    let key = e.key.toUpperCase();
    if (lanes.includes(key)) {
        keyStates[key] = false;
    }
});

// 판정 체크
function checkJudgment(key) {
    let hit = false;
    for (let i = 0; i < notes.length; i++) {
        let note = notes[i];
        if (note.lane === key) {
            let distance = Math.abs(note.y - judgmentLineY);
            if (distance <= tolerance) {
                // Perfect 판정
                score += 100;
                combo += 1;
                addJudgmentEffect(key, "PERFECT", "#00FFCC");
                notes.splice(i, 1);
                hit = true;
                break;
            } else if (distance <= tolerance * 2) {
                // Good 판정
                score += 50;
                combo += 1;
                addJudgmentEffect(key, "GOOD", "#FFCC00");
                notes.splice(i, 1);
                hit = true;
                break;
            }
        }
    }
    
    // 알맞은 키(QWER)를 눌렀으나 해당 레인에 맞출 노트가 없었던 경우 (허공에 삽질)
    if (!hit) {
        score = Math.max(0, score - 30); // 0점 미만으로 안 떨어지게 방지하려면 Math.max 사용 (음수 허용하려면 빼기만 설정)
        combo = 0;
        addJudgmentEffect(key, "MISS", "#FF3333");
    }
    
    updateDOM();
}

// QWER 이외의 잘못된 키 처리
function triggerWrongKey() {
    score = Math.max(0, score - 30); // 30점 감점
    combo = 0;
    // 무작위 레인 위치에 MISS 표시를 띄워 잘못 눌렀음을 알림
    const randomLane = lanes[Math.floor(Math.random() * lanes.length)];
    addJudgmentEffect(randomLane, "WRONG KEY", "#FF3333");
    updateDOM();
}

// 스코어 및 콤보 보드 갱신
function updateDOM() {
    document.getElementById("score").innerText = score;
    document.getElementById("combo").innerText = combo > 0 ? combo + " COMBO" : "";
}

function addJudgmentEffect(key, text, color) {
    judgmentTexts.push({
        x: laneX[key],
        y: judgmentLineY - 50,
        text: text,
        color: color,
        alpha: 1.0
    });
}

// 게임 메인 루프
function update() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // 1. 레인 가이드라인 그리기
    lanes.forEach(lane => {
        ctx.strokeStyle = "#333";
        ctx.lineWidth = 1;
        ctx.beginPath();
        ctx.moveTo(laneX[lane] - laneWidth/2, 0);
        ctx.lineTo(laneX[lane] - laneWidth/2, canvas.height);
        ctx.stroke();
        
        // 키 누름 효과
        if (keyStates[lane]) {
            ctx.fillStyle = "rgba(255, 255, 255, 0.15)";
            ctx.fillRect(laneX[lane] - laneWidth/2, 0, laneWidth, canvas.height);
