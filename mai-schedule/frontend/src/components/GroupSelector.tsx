import React, { useEffect, useState } from "react";
import styled from "styled-components";
import { motion } from "framer-motion";
import { api } from "../services/api";
import type { Group } from "../services/api";

const SelectorContainer = styled(motion.div)`
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border-radius: 20px;
  padding: 2rem;
  box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
  border: 1px solid rgba(255, 255, 255, 0.18);
  width: 90%;
  max-width: 600px;
  margin: 2rem auto;
`;

const Title = styled.h2`
  color: white;
  text-align: center;
  margin-bottom: 1.5rem;
  font-size: 1.8rem;
  font-weight: 600;
`;

const SelectContainer = styled.div`
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  margin-bottom: 2rem;
`;

const Select = styled.select`
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 10px;
  padding: 1rem;
  color: white;
  font-size: 1.1rem;
  cursor: pointer;
  transition: all 0.3s ease;
  width: 100%;

  &:hover {
    background: rgba(255, 255, 255, 0.2);
  }

  option {
    background: #764ba2;
    color: white;
  }
`;

const Label = styled.label`
  color: white;
  font-size: 1.1rem;
  margin-bottom: 0.5rem;
  display: block;
`;

const Button = styled(motion.button)`
  background: rgba(255, 255, 255, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: 10px;
  padding: 1rem 2rem;
  color: white;
  font-size: 1.1rem;
  cursor: pointer;
  transition: all 0.3s ease;
  width: 100%;

  &:hover {
    background: rgba(255, 255, 255, 0.3);
  }

  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
`;

const ErrorMessage = styled.div`
  color: #ff6b6b;
  text-align: center;
  margin-top: 1rem;
  font-size: 1.1rem;
`;

interface GroupSelectorProps {
  institute: number;
  onSelect: (course: number, group: string) => void;
}

const GroupSelector: React.FC<GroupSelectorProps> = ({
  institute,
  onSelect,
}) => {
  const [selectedCourse, setSelectedCourse] = useState<number>(1);
  const [selectedGroup, setSelectedGroup] = useState<string>("");
  const [groups, setGroups] = useState<Group[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchGroups = async () => {
      try {
        const data = await api.getGroups(institute.toString());
        setGroups(data);
        setError(null);
      } catch (err) {
        setError("Не удалось загрузить список групп");
        console.error(err);
      }
    };

    fetchGroups();
  }, [institute]);

  const handleSubmit = () => {
    if (selectedCourse && selectedGroup) {
      onSelect(selectedCourse, selectedGroup);
    }
  };

  const filteredGroups = groups.filter(
    (group) => group.course === selectedCourse
  );

  return (
    <SelectorContainer
      initial={{ opacity: 0, y: -20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
    >
      <Title>Выберите курс и группу</Title>
      <SelectContainer>
        <div>
          <Label>Курс</Label>
          <Select
            value={selectedCourse}
            onChange={(e) => setSelectedCourse(Number(e.target.value))}
          >
            {[1, 2, 3, 4].map((course) => (
              <option key={course} value={course}>
                {course} курс
              </option>
            ))}
          </Select>
        </div>
        <div>
          <Label>Группа</Label>
          <Select
            value={selectedGroup}
            onChange={(e) => setSelectedGroup(e.target.value)}
          >
            <option value="">Выберите группу</option>
            {filteredGroups.map((group) => (
              <option key={group.id} value={group.id}>
                {group.name}
              </option>
            ))}
          </Select>
        </div>
      </SelectContainer>
      <Button
        onClick={handleSubmit}
        whileHover={{ scale: 1.02 }}
        whileTap={{ scale: 0.98 }}
        disabled={!selectedGroup}
      >
        Показать расписание
      </Button>
      {error && <ErrorMessage>{error}</ErrorMessage>}
    </SelectorContainer>
  );
};

export default GroupSelector;
