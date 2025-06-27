export interface Intern {
  id: number;
  name: string;
  internType: string;
  siteLogoUrl: string; // URL or path to the logo
  internPictureUrl: string; // URL or path to the picture
  subtitle: string;
  description: string;
  showOnPlatform: string[]; // e.g., ['linkedin.com', 'gmail.com']
}

export const interns: Intern[] = [
  {
    id: 1,
    name: 'Alex',
    internType: 'LinkedIn Intern',
    siteLogoUrl: '/assets/linkedin-logo.svg', // Placeholder path
    internPictureUrl: '/intern_headshots/intern_1_pixar.png', // Placeholder path
    subtitle: 'Drafts LinkedIn replies',
    description: "I’ll draft LinkedIn replies for you, based on how you usually bark—I mean, write—and the chats you’ve had before. If someone’s thrown that stick your way already, I’ll fetch your usual answer!",
    showOnPlatform: ['linkedin.com'],
  },
  {
    id: 2,
    name: 'Ben',
    internType: 'LinkedIn Intern',
    siteLogoUrl: '/assets/linkedin-logo.svg', // Placeholder path
    internPictureUrl: '/intern_headshots/intern_2_pixar.png', // Placeholder path
    subtitle: 'Analyzes writing style',
    description: "I'll quietly observe your past messages, analyze your writing style, and make sure every message I draft sounds unmistakably like you. Naturally. 🐱",
    showOnPlatform: ['linkedin.com'],
  },
  {
    id: 3,
    name: 'Charlie',
    internType: 'LinkedIn Intern',
    siteLogoUrl: '/assets/linkedin-logo.svg', // Placeholder path
    internPictureUrl: '/intern_headshots/intern_3_pixar.png', // Placeholder path
    subtitle: 'Researches prospects',
    description: "I’ll zip around LinkedIn, gather intel like pollen, and spot bits of common ground to help you start conversations that stick. 🐝" ,
    showOnPlatform: ['linkedin.com'],
  },
]; 