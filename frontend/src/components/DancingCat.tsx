import React from "react";
import styled, { keyframes } from "styled-components";

const dance = keyframes`
  0% { transform: rotate(0deg) translateY(0); }
  25% { transform: rotate(10deg) translateY(-5px); }
  50% { transform: rotate(0deg) translateY(0); }
  75% { transform: rotate(-10deg) translateY(-5px); }
  100% { transform: rotate(0deg) translateY(0); }
`;

const CatContainer = styled.div`
  position: fixed;
  top: 20px;
  right: 20px;
  z-index: 1000;
  cursor: pointer;
  animation: ${dance} 1s infinite;
  transition: transform 0.3s ease;

  &:hover {
    transform: scale(1.1);
  }
`;

const DancingCat: React.FC = () => {
  return (
    <CatContainer>
      <svg
        width="50"
        height="50"
        viewBox="0 0 24 24"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
      >
        {/* Тело кота */}
        <path
          d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2z"
          fill="#fff"
        />
        {/* Уши */}
        <path
          d="M8 7l-2-3h4l2 3M16 7l2-3h-4l-2 3"
          stroke="#fff"
          strokeWidth="2"
          strokeLinecap="round"
        />
        {/* Глаза */}
        <circle cx="9" cy="10" r="1" fill="#764ba2" />
        <circle cx="15" cy="10" r="1" fill="#764ba2" />
        {/* Нос */}
        <path d="M12 12c0 1-1 2-2 2s-2-1-2-2 1-2 2-2 2 1 2 2z" fill="#764ba2" />
        {/* Усы */}
        <path
          d="M8 13c-2 0-3 1-3 2M16 13c2 0 3 1 3 2"
          stroke="#fff"
          strokeWidth="1"
          strokeLinecap="round"
        />
      </svg>
    </CatContainer>
  );
};

export default DancingCat;
