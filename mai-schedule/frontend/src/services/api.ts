const API_BASE_URL = "http://localhost:8000/api";

export interface Institute {
  id: string;
  name: string;
}

export interface Group {
  id: string;
  name: string;
  course: number;
}

export interface Lesson {
  time: string;
  name: string;
  teacher: string;
  room: string;
}

export interface Schedule {
  monday: Lesson[];
  tuesday: Lesson[];
  wednesday: Lesson[];
  thursday: Lesson[];
  friday: Lesson[];
  saturday: Lesson[];
  sunday: Lesson[];
}

export const api = {
  async getInstitutes(): Promise<Institute[]> {
    const response = await fetch(`${API_BASE_URL}/institutes`);
    if (!response.ok) {
      throw new Error("Failed to fetch institutes");
    }
    return response.json();
  },

  async getGroups(instituteId: string, course?: number): Promise<Group[]> {
    const url = new URL(`${API_BASE_URL}/groups/${instituteId}`);
    if (course) {
      url.searchParams.append("course", course.toString());
    }
    const response = await fetch(url.toString());
    if (!response.ok) {
      throw new Error("Failed to fetch groups");
    }
    return response.json();
  },

  async getSchedule(groupId: string): Promise<Schedule> {
    const response = await fetch(`${API_BASE_URL}/schedule/${groupId}`);
    if (!response.ok) {
      throw new Error("Failed to fetch schedule");
    }
    return response.json();
  },
};
