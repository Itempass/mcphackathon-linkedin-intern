import { DraftMessage } from '../../../../api/backend';

// Mock draft data for testing Phase 1 and 2 implementations
export const mockDraftMessages: DraftMessage[] = [
  {
    thread_name: "Sarah Johnson",
    draft_message_id: "draft_001",
    draft_message_content: "Hi Sarah! Thanks for reaching out about the marketing collaboration. I'd love to discuss this further and explore how we can work together on this exciting project."
  },
  {
    thread_name: "Michael Chen", 
    draft_message_id: "draft_002",
    draft_message_content: "Hey Michael, I saw your post about the new product launch. Congratulations! The design looks fantastic and I'm sure it will be a huge success."
  },
  {
    thread_name: "Emily Rodriguez",
    draft_message_id: "draft_003", 
    draft_message_content: "Emily, thank you for the detailed feedback on the proposal. I've incorporated your suggestions and I think the revised version addresses all your concerns. Let me know what you think!"
  },
  {
    thread_name: "David Kim",
    draft_message_id: "draft_004",
    draft_message_content: "David, I hope you're doing well! I wanted to follow up on our conversation from last week about the potential partnership opportunity."
  },
  {
    thread_name: "Lisa Thompson", 
    draft_message_id: "draft_005",
    draft_message_content: "Hi Lisa! I just wanted to reach out and say thank you for the introduction to the team at TechCorp. The meeting went really well and I'm excited about the possibilities moving forward."
  }
];

// Function to simulate API delay
export const getMockDrafts = async (): Promise<{ draft_messages: DraftMessage[] }> => {
  // Simulate network delay
  await new Promise(resolve => setTimeout(resolve, 800));
  
  return {
    draft_messages: mockDraftMessages
  };
}; 