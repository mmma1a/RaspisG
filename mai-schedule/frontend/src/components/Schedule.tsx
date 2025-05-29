import React, { useState, useEffect } from "react";
import styled from "styled-components";
import { motion } from "framer-motion";
import { format, addDays, subDays, isSameDay } from "date-fns";
import { ru } from "date-fns/locale";
import { api } from "../services/api";
import type { Schedule as ScheduleType, Lesson } from "../services/api";

const ScheduleContainer = styled(motion.div)`
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border-radius: 20px;
  padding: 2rem;
  box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
  border: 1px solid rgba(255, 255, 255, 0.18);
  width: 90%;
  max-width: 1200px;
  margin: 2rem auto;
`;

const NavigationContainer = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  padding: 0 1rem;
`;

const NavButton = styled(motion.button)`
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 10px;
  padding: 0.8rem 1.5rem;
  color: white;
  font-size: 1rem;
  cursor: pointer;
  transition: all 0.3s ease;

  &:hover {
    background: rgba(255, 255, 255, 0.2);
  }

  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
`;

const CurrentDate = styled.div`
  color: white;
  font-size: 1.2rem;
  font-weight: 500;
`;

const GroupInfo = styled.div`
  color: white;
  text-align: center;
  margin-bottom: 2rem;
  font-size: 1.2rem;
`;

const DayContainer = styled.div<{ isToday: boolean }>`
  margin-bottom: 2rem;
  padding: 1.5rem;
  background: ${(props) =>
    props.isToday ? "rgba(255, 255, 255, 0.15)" : "rgba(255, 255, 255, 0.05)"};
  border-radius: 15px;
  transition: all 0.3s ease;
  border: ${(props) =>
    props.isToday ? "2px solid rgba(255, 255, 255, 0.3)" : "none"};

  &:hover {
    transform: translateY(-5px);
    box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
  }
`;

const DayTitle = styled.h2`
  color: white;
  margin-bottom: 1rem;
  font-size: 1.5rem;
  font-weight: 600;
`;

const Lesson = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  margin: 0.5rem 0;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 10px;
  transition: all 0.3s ease;

  &:hover {
    background: rgba(255, 255, 255, 0.2);
  }
`;

const LessonInfo = styled.div`
  flex: 1;
`;

const LessonTime = styled.span`
  color: white;
  font-weight: 500;
  margin-right: 1rem;
`;

const LessonName = styled.span`
  color: white;
  font-weight: 400;
`;

const LessonRoom = styled.span`
  color: rgba(255, 255, 255, 0.7);
  margin-left: 1rem;
`;

const ErrorMessage = styled.div`
  color: #ff6b6b;
  text-align: center;
  margin-top: 1rem;
  font-size: 1.1rem;
`;

interface ScheduleProps {
  institute: number;
  course: number | null;
  group: string;
}

const dayMapping: { [key: string]: string } = {
  monday: "Понедельник",
  tuesday: "Вторник",
  wednesday: "Среда",
  thursday: "Четверг",
  friday: "Пятница",
  saturday: "Суббота",
  sunday: "Воскресенье",
};

const Schedule: React.FC<ScheduleProps> = ({ institute, course, group }) => {
  const [currentDate, setCurrentDate] = useState(new Date());
  const [selectedDate, setSelectedDate] = useState(new Date());
  const [schedule, setSchedule] = useState<ScheduleType | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchSchedule = async () => {
      try {
        const data = await api.getSchedule(group);
        setSchedule(data);
        setError(null);
      } catch (err) {
        setError("Не удалось загрузить расписание");
        console.error(err);
      }
    };

    fetchSchedule();
  }, [group]);

  const handlePrevDay = () => {
    setSelectedDate((prev) => subDays(prev, 1));
  };

  const handleNextDay = () => {
    setSelectedDate((prev) => addDays(prev, 1));
  };

  const handleToday = () => {
    setSelectedDate(new Date());
  };

  const getDayIndex = (date: Date) => {
    const day = date.getDay();
    return day === 0 ? 6 : day - 1; // Преобразуем воскресенье (0) в 6
  };

  const getDayKey = (date: Date): keyof ScheduleType => {
    const days = [
      "sunday",
      "monday",
      "tuesday",
      "wednesday",
      "thursday",
      "friday",
      "saturday",
    ];
    return days[date.getDay()] as keyof ScheduleType;
  };

  const currentDayKey = getDayKey(selectedDate);
  const currentDayLessons = schedule ? schedule[currentDayKey] : [];

  return (
    <ScheduleContainer
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
    >
      <GroupInfo>
        ИУ-{institute}, {course} курс, группа {group}
      </GroupInfo>
      <NavigationContainer>
        <NavButton
          onClick={handlePrevDay}
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
        >
          ← Предыдущий день
        </NavButton>
        <CurrentDate>
          {format(selectedDate, "d MMMM yyyy", { locale: ru })}
        </CurrentDate>
        <NavButton
          onClick={handleNextDay}
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
        >
          Следующий день →
        </NavButton>
      </NavigationContainer>

      <DayContainer isToday={isSameDay(selectedDate, currentDate)}>
        <DayTitle>{dayMapping[currentDayKey]}</DayTitle>
        {error ? (
          <ErrorMessage>{error}</ErrorMessage>
        ) : currentDayLessons.length > 0 ? (
          currentDayLessons.map((lesson, lessonIndex) => (
            <Lesson key={lessonIndex}>
              <LessonInfo>
                <LessonTime>{lesson.time}</LessonTime>
                <LessonName>{lesson.name}</LessonName>
                <LessonRoom>{lesson.room}</LessonRoom>
              </LessonInfo>
            </Lesson>
          ))
        ) : (
          <div
            style={{
              textAlign: "center",
              color: "rgba(255, 255, 255, 0.7)",
              padding: "2rem",
            }}
          >
            Нет занятий
          </div>
        )}
      </DayContainer>
    </ScheduleContainer>
  );
};

export default Schedule;
