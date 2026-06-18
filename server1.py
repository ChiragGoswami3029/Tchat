import asyncio
import websockets
from datetime import datetime

connected_clients={} # stores connected clients in key-value pairs (username:websocket)

def get_time():
    return datetime.now().strftime("%H:%M")

  
async def Circulate(message, exclude=None):
    for username, client in list(connected_clients.items()):
        if client != exclude:
            try:
              await client.send(message)
            except:
             pass
           
async def handler(websocket):
    username = None
    try:
         
         username = await websocket.recv()
         username= username.strip()

         if username in connected_clients:
            await websocket.send("Error:Username already taken. Try different username.")
            return
    
         connected_clients[username]= websocket
         join_msg= f"[{get_time()}]***{username} has joined the chat"
         print(join_msg)
         await Circulate(join_msg)
         await websocket.send(f"[{get_time()}] Welcome {username}! Type/help to see commands.")


         async for message in websocket:
             message= message.strip()
             if not message:
              continue
       


             if message== "/help":
       
                help_txt=(f"[{get_time()}]*** Commands:\n"
                 "  /users        -- See who is online\n"
                 "  /dm user msg  --  Send private msg\n"
                 "  /nick newname -- Change your username\n"
                 "  /quit         -- Leave the chat" 
                 )
                await websocket.send(help_txt)
             elif message.startswith("/dm "):
                parts = message.split(" ", 2)
                if len(parts) < 3:
                    await websocket.send(f"[{get_time()}] Usage: /dm username message")
                else:
                    target = parts[1]
                    dm_text = parts[2]
                    if target not in connected_clients:
                        await websocket.send(f"[{get_time()}] User '{target}' not found.")
                    elif target == username:
                        await websocket.send(f"[{get_time()}] You cannot DM yourself.")
                    else:
                        await connected_clients[target].send(f"[{get_time()}] [DM from {username}]: {dm_text}")
                        await websocket.send(f"[{get_time()}] [DM to {target}]: {dm_text}")
             elif message == "/users":
               user_list= ", ".join(connected_clients.keys())
               await websocket.send(f"[{get_time()}] Online Now:{user_list} ")

             elif  message.startswith("/nick"):
                  new_name= message.split("  ", 1)[1].strip()
                  if not new_name:
                   await websocket.send(f"[{get_time()}] Usage: /nick newname")
 
                  elif new_name in connected_clients:
                    await websocket.send(f"[{get_time()}] Username '{new_name}' is already exists!")

                  else:
                    old_name= username
                    connected_clients[new_name] = connected_clients.pop(old_name)
                    username = new_name
                    rename_msg= f"[{get_time()}]*** {old_name} is now {new_name}!"
                    print(rename_msg)
                    await Circulate(rename_msg)

             elif  message == "/quit":
                await websocket.send(f"[{get_time()}] Goodbye {username}!")
                break
             elif message.startswith("/"):
                await websocket.send(f"[{get_time()}] Unknown command. Type /help for commands.")

             else:
                # Regular message — broadcast to everyone
                chat_msg = f"[{get_time()}] {username}: {message}"
                print(chat_msg)
                await Circulate(chat_msg)
           
           
    except websockets.exceptions.ConnectionClosed:
          pass
    
    finally :
          
          if username and username in connected_clients:
             del connected_clients[username]
             leave_msg =f"[{get_time()}]***{username} has left the Chat***"
             print(leave_msg)
             await Circulate(leave_msg)


async def main():
   print("Pychat server started on ws://localhost:8765")
   print("Waiting for users to connect...\n")
   async with websockets.serve(handler,"localhost", 8765):
       await asyncio.Future()

       
asyncio.run(main())



