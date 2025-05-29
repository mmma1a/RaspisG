import React, { useEffect, useState } from "react";
import styled from "styled-components";
import { motion } from "framer-motion";
import { api } from "../services/api";
import type { Institute } from "../services/api";

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

const InstituteGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  gap: 1rem;
  margin-bottom: 2rem;
`;

const InstituteButton = styled(motion.button)`
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 10px;
  padding: 1rem;
  color: white;
  font-size: 1.1rem;
  cursor: pointer;
  transition: all 0.3s ease;

  &:hover {
    background: rgba(255, 255, 255, 0.2);
  }

  &.selected {
    background: rgba(255, 255, 255, 0.3);
    border-color: rgba(255, 255, 255, 0.4);
  }
`;

const ErrorMessage = styled.div`
  color: #ff6b6b;
  text-align: center;
  margin-top: 1rem;
  font-size: 1.1rem;
  padding: 1rem;
  background: rgba(255, 107, 107, 0.1);
  border-radius: 10px;
  border: 1px solid rgba(255, 107, 107, 0.3);
`;

const LoadingMessage = styled.div`
  color: white;
  text-align: center;
  margin-top: 1rem;
  font-size: 1.1rem;
`;

interface InstituteSelectorProps {
  onSelect: (institute: number) => void;
  selectedInstitute: number | null;
}

const InstituteSelector: React.FC<InstituteSelectorProps> = ({
  onSelect,
  selectedInstitute,
}) => {
  const [institutes, setInstitutes] = useState<Institute[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchInstitutes = async () => {
      try {
        setIsLoading(true);
        setError(null);
        console.log("Fetching institutes...");
        const data = await api.getInstitutes();
        console.log("Received institutes:", data);
        setInstitutes(data);
      } catch (err) {
        console.error("Error fetching institutes:", err);
        setError(
          err instanceof Error
            ? err.message
            : "Не удалось загрузить список институтов"
        );
      } finally {
        setIsLoading(false);
      }
    };

    fetchInstitutes();
  }, []);

  return (
    <SelectorContainer
      initial={{ opacity: 0, y: -20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
    >
      <Title>Выберите институт</Title>
      {isLoading ? (
        <LoadingMessage>Загрузка списка институтов...</LoadingMessage>
      ) : error ? (
        <ErrorMessage>
          {error}
          <br />
          <small>
            Проверьте, что бэкенд запущен и доступен по адресу
            http://localhost:8000
          </small>
        </ErrorMessage>
      ) : (
        <InstituteGrid>
          {institutes.map((institute) => (
            <InstituteButton
              key={institute.id}
              onClick={() => onSelect(parseInt(institute.id))}
              className={
                selectedInstitute === parseInt(institute.id) ? "selected" : ""
              }
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              {institute.name}
            </InstituteButton>
          ))}
        </InstituteGrid>
      )}
    </SelectorContainer>
  );
};

export default InstituteSelector;
