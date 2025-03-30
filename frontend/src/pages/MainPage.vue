
<template>
	<div class="container">
		<div class="header">
			<i class="fas fa-oil-can"></i>
			<h1>Ввод данных скважины</h1>
			<p>Пожалуйста, заполните все необходимые параметры для анализа</p>
		</div>

		<div class="form-container">
			<form id="wellForm">
				<div class="row">
					<div class="col">
						<div class="form-group">
							<label for="wellName">Название скважины</label>
							<input type="text" id="wellName" class="form-control"
								placeholder="Например: Северная-125">
							<i class="fas fa-font input-icon"></i>
						</div>
					</div>
					<div class="col">
						<div class="form-group">
							<label for="wellType">Тип скважины</label>
							<select id="wellType" class="form-control">
								<option value="" disabled selected>Выберите тип</option>
								<option value="oil">Нефтяная</option>
								<option value="gas">Газовая</option>
								<option value="injection">Нагнетательная</option>
								<option value="observation">Наблюдательная</option>
							</select>
						</div>
					</div>
				</div>

				<div class="row">
					<div class="col">
						<div class="form-group">
							<label for="pressure">Давление на устье (P<sub>у</sub>)</label>
							<input type="number" id="pressure" class="form-control" placeholder="Введите давление"
								step="0.01">
							<span class="unit">атм</span>
							<div class="error-message" id="pressure-error">Пожалуйста, введите корректное значение
								давления</div>
						</div>
					</div>
					<div class="col">
						<div class="form-group">
							<label for="bottomPressure">Забойное давление (P<sub>з</sub>)</label>
							<input type="number" id="bottomPressure" class="form-control"
								placeholder="Введите забойное давление" step="0.01">
							<span class="unit">атм</span>
							<div class="error-message" id="bottomPressure-error">Пожалуйста, введите корректное
								значение забойного давления</div>
						</div>
					</div>
				</div>

				<div class="row">
					<div class="col">
						<div class="form-group">
							<label for="depth">Глубина скважины (H)</label>
							<input type="number" id="depth" class="form-control" placeholder="Введите глубину">
							<span class="unit">м</span>
							<div class="error-message" id="depth-error">Пожалуйста, введите корректное значение
								глубины</div>
						</div>
					</div>
					<div class="col">
						<div class="form-group">
							<label for="temperature">Температура на забое</label>
							<input type="number" id="temperature" class="form-control"
								placeholder="Введите температуру" step="0.1">
							<span class="unit">°C</span>
						</div>
					</div>
				</div>

				<div class="form-group">
					<label for="production">Дебит (Q)</label>
					<input type="number" id="production" class="form-control" placeholder="Введите дебит">
					<span class="unit">м³/сут</span>
					<div class="form-note">Для нефтяных скважин - в тоннах, для газовых - в кубометрах</div>
				</div>

				<div class="form-group">
					<label for="waterCut">Обводнённость (W)</label>
					<div style="display: flex; align-items: center;">
						<input type="range" id="waterCut" class="form-control" min="0" max="100" value="0"
							style="flex: 1; padding: 0;">
						<span id="waterCutValue"
							style="margin-left: 15px; min-width: 40px; text-align: center;">0%</span>
					</div>
				</div>

				<div class="form-group">
					<label for="comments">Комментарии</label>
					<textarea id="comments" class="form-control" rows="3"
						placeholder="Дополнительная информация..."></textarea>
				</div>

				<div class="form-group" style="margin-top: 30px;">
					<button type="submit" class="btn btn-secondary btn-animate">
						<i class="fas fa-save" style="margin-right: 10px;"></i> Сохранить данные
					</button>
				</div>
			</form>
		</div>
	</div>
</template>
<script setup> console.log(111) </script>
<style scoped>
:root {
  --primary: #3498db;
  --primary-dark: #2980b9;
  --secondary: #2ecc71;
  --danger: #e74c3c;
  --light: #ecf0f1;
  --dark: #34495e;
  --gray: #95a5a6;
}

* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

body {
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  min-height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 20px;
}

.container {
  background: white;
  border-radius: 15px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
  width: 100%;
  max-width: 800px;
  overflow: hidden;
  animation: fadeIn 0.5s ease-out;
}

@keyframes fadeIn {
  from {
	opacity: 0;
	transform: translateY(20px);
  }

  to {
	opacity: 1;
	transform: translateY(0);
  }
}

.header {
  background: linear-gradient(to right, var(--primary), var(--primary-dark));
  color: white;
  padding: 25px;
  text-align: center;
  position: relative;
}

.header h1 {
  font-size: 28px;
  margin-bottom: 10px;
}

.header p {
  opacity: 0.9;
  font-size: 16px;
}

.header i {
  position: absolute;
  top: 20px;
  right: 20px;
  font-size: 40px;
  opacity: 0.2;
}

.form-container {
  padding: 30px;
}

.form-group {
  margin-bottom: 25px;
  position: relative;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: 600;
  color: var(--dark);
}

.form-control {
  width: 100%;
  padding: 15px 20px;
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  font-size: 16px;
  transition: all 0.3s;
  background-color: #f9f9f9;
}

.form-control:focus {
  border-color: var(--primary);
  box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.2);
  outline: none;
  background-color: white;
}

.form-control::placeholder {
  color: var(--gray);
  opacity: 0.5;
}

.input-icon {
  position: absolute;
  right: 15px;
  top: 42px;
  color: var(--gray);
}

.unit {
  position: absolute;
  right: 15px;
  top: 42px;
  color: var(--gray);
  font-size: 14px;
  background: #f1f1f1;
  padding: 0 10px;
  border-radius: 5px;
}

.btn {
  display: inline-block;
  background: var(--primary);
  color: white;
  border: none;
  padding: 15px 30px;
  border-radius: 8px;
  cursor: pointer;
  font-size: 16px;
  font-weight: 600;
  transition: all 0.3s;
  width: 100%;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.btn:hover {
  background: var(--primary-dark);
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
}

.btn-secondary {
  background: var(--secondary);
}

.btn-secondary:hover {
  background: #27ae60;
}

.row {
  display: flex;
  gap: 20px;
}

.col {
  flex: 1;
}

.form-note {
  font-size: 14px;
  color: var(--gray);
  margin-top: 5px;
  font-style: italic;
}

@media (max-width: 768px) {
  .row {
	flex-direction: column;
	gap: 15px;
  }

  .header h1 {
	font-size: 24px;
  }
}

/* Анимация для кнопки */
@keyframes pulse {
  0% {
	transform: scale(1);
  }

  50% {
	transform: scale(1.05);
  }

  100% {
	transform: scale(1);
  }
}

.btn-animate {
  animation: pulse 2s infinite;
}

/* Стили для валидации */
.error {
  border-color: var(--danger) !important;
}

.error-message {
  color: var(--danger);
  font-size: 13px;
  margin-top: 5px;
  display: none;
}


  /* Стили для выпадающего списка */
  select.form-control {
    appearance: none;
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='16' height='16' fill='%2395a5a6' viewBox='0 0 16 16'%3E%3Cpath d='M7.247 11.14 2.451 5.658C1.885 5.013 2.345 4 3.204 4h9.592a1 1 0 0 1 .753 1.659l-4.796 5.48a1 1 0 0 1-1.506 0z'/%3E%3C/svg%3E");
    background-repeat: no-repeat;
    background-position: right 15px center;
    padding-right: 40px;
  }
</style>

