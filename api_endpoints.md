## endpoint POST /send-messages/
request body parameters:
*user_id: string 
*thread_name: string 
*messages: Array[{
    message_id: string (hash of sender name, date+time, message content), 
    sender_name: string (name of sender), 
    date: Date (date of message sent), 
    time: Time (time of message sent), 
    message_content: string
}]

response: 
- 202 ACCEPTED


## endpoint POST /process-feedback/
request body parameters:
*user_id: string 
*draft_message_id: string 
*feedback: string

response: 
- 202 ACCEPTED


## endpoint POST /reject-draft/
request body parameters: 
*user_id: string 
*draft_message_id: string 

response: 
- 200 OK

## endpoint GET /draft_messages/
request body parameters: 
*user_id: string 

response: 
- 200 OK
    - draft_messages: Array[
        {
            thread_name: string,
            draft_message_id: string, 
            draft_message_content: string
        }
    ]





