import type { Course } from '../../types/course'

export type Term = 'Fall' | 'Spring' | 'Summer'
export type SemesterCourses = Record<string, Course[]>
export type SemesterOption = { key: string; label: string }
