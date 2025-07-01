// script.js
document.addEventListener('DOMContentLoaded', () => {
  const dateInput = document.getElementById('date-input');
  const calendar = document.getElementById('calendar');
  const prevMonth = document.getElementById('prev-month');
  const nextMonth = document.getElementById('next-month');
  const monthYear = document.getElementById('month-year');
  const calendarDays = document.getElementById('calendar-days');
  const cancelBtn = document.getElementById('cancel-btn');
  const applyBtn = document.getElementById('apply-btn');

  let selectedDates = [];
  let currentMonth = new Date().getMonth();
  let currentYear = new Date().getFullYear();

  dateInput.addEventListener('click', () => {
      calendar.style.display = 'block';
      renderCalendar(currentMonth, currentYear);
  });

  prevMonth.addEventListener('click', () => {
      currentMonth--;
      if (currentMonth < 0) {
          currentMonth = 11;
          currentYear--;
      }
      renderCalendar(currentMonth, currentYear);
  });

  nextMonth.addEventListener('click', () => {
      currentMonth++;
      if (currentMonth > 11) {
          currentMonth = 0;
          currentYear++;
      }
      renderCalendar(currentMonth, currentYear);
  });

  cancelBtn.addEventListener('click', () => {
      selectedDates = [];
      calendar.style.display = 'none';
  });

  applyBtn.addEventListener('click', () => {
      dateInput.value = selectedDates.join(', ');
      calendar.style.display = 'none';
  });

  function renderCalendar(month, year) {
      calendarDays.innerHTML = '';
      monthYear.textContent = `${new Date(year, month).toLocaleString('default', { month: 'long' })} ${year}`;

      const firstDay = new Date(year, month, 1).getDay();
      const daysInMonth = new Date(year, month + 1, 0).getDate();

      for (let i = 0; i < firstDay; i++) {
          calendarDays.innerHTML += '<span></span>';
      }

      for (let i = 1; i <= daysInMonth; i++) {
          const day = document.createElement('span');
          day.textContent = i;
          day.addEventListener('click', () => {
              if (selectedDates.includes(i)) {
                  selectedDates = selectedDates.filter(date => date !== i);
                  day.classList.remove('selected');
              } else {
                  selectedDates.push(i);
                  day.classList.add('selected');
              }
          });
          calendarDays.appendChild(day);
      }
  }
});
