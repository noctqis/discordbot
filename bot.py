import discord
from discord.ext import commands, tasks
import asyncio

# Set up bot with intents
intents = discord.Intents.default()
intents.members = True  # Needed to assign roles
bot = commands.Bot(command_prefix="!", intents=intents)

# Store channel IDs and role ID
approved_oc_channel_id = None
roleplayer_role_id = None
rumor_channel_id = None
rumor_pool = []

# Ensure bot is ready before using application commands
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    send_rumors.start()  # Start the rumor sending loop
    try:
        synced = await bot.tree.sync()  # Sync slash commands
        print(f"Synced {len(synced)} commands.")
    except Exception as e:
        print(f"Failed to sync commands: {e}")

### **🛠️ Admin Command: Set Approved OC Channel**
@bot.tree.command(name="set_approved_channel", description="Set the channel where approved OCs are announced (Admin only).")
@commands.has_permissions(administrator=True)
async def set_approved_channel(interaction: discord.Interaction, channel: discord.TextChannel):
    global approved_oc_channel_id
    approved_oc_channel_id = channel.id
    await interaction.response.send_message(f"✅ Approved OC channel set to {channel.mention}", ephemeral=True)

### **✅ Approve OC Command**
@bot.tree.command(name="approve_oc", description="Approve an OC and notify the user (Admin only).")
@commands.has_permissions(administrator=True)
async def approve_oc(interaction: discord.Interaction, user: discord.Member, forum_link: str):
    global approved_oc_channel_id, roleplayer_role_id

    if approved_oc_channel_id is None:
        await interaction.response.send_message("⚠️ No approved OC channel set. Use `/set_approved_channel` first.", ephemeral=True)
        return
    
    approved_channel = bot.get_channel(approved_oc_channel_id)
    if not approved_channel:
        await interaction.response.send_message("⚠️ Approved OC channel is invalid. Please reset it.", ephemeral=True)
        return

    # Assign roleplayer role if it's set
    if roleplayer_role_id:
        role = interaction.guild.get_role(roleplayer_role_id)
        if role:
            await user.add_roles(role)

    # Send approval message
    await approved_channel.send(f"✅ {user.mention} {forum_link} has been approved!")
    await interaction.response.send_message(f"OC approved and announced in {approved_channel.mention}!", ephemeral=True)

### **🛠️ Admin Command: Set Roleplayer Role**
@bot.tree.command(name="set_roleplayer_role", description="Set the role given to approved OCs (Admin only).")
@commands.has_permissions(administrator=True)
async def set_roleplayer_role(interaction: discord.Interaction, role: discord.Role):
    global roleplayer_role_id
    roleplayer_role_id = role.id
    await interaction.response.send_message(f"✅ Roleplayer role set to {role.mention}", ephemeral=True)

### **🗣️ Submit an Anonymous Rumor**
@bot.tree.command(name="rumor", description="Submit an anonymous rumor.")
async def rumor(interaction: discord.Interaction, text: str):
    global rumor_pool
    rumor_pool.append(text)
    await interaction.response.send_message("✅ Your rumor has been stored!", ephemeral=True)

### **🛠️ Admin Command: Set Rumor Channel**
@bot.tree.command(name="set_rumor_channel", description="Set the channel where rumors will be sent (Admin only).")
@commands.has_permissions(administrator=True)
async def set_rumor_channel(interaction: discord.Interaction, channel: discord.TextChannel):
    global rumor_channel_id
    rumor_channel_id = channel.id
    await interaction.response.send_message(f"✅ Rumor channel set to {channel.mention}", ephemeral=True)

### **⏳ Background Task: Send Rumors Every 4 Hours**
@tasks.loop(hours=4)
async def send_rumors():
    global rumor_channel_id, rumor_pool

    if rumor_channel_id is None or not rumor_pool:
        return  # Do nothing if no channel is set or no rumors exist

    channel = bot.get_channel(rumor_channel_id)
    if channel:
        rumor = rumor_pool.pop(0)  # Get and remove the first rumor in the list
        await channel.send(f"🕵️‍♂️ Rumor: {rumor}")

### **🛠️ Admin Command: Test a Rumor**
@bot.tree.command(name="test", description="Send a test rumor immediately (Admin only).")
@commands.has_permissions(administrator=True)
async def test_rumor(interaction: discord.Interaction, text: str):
    global rumor_channel_id

    if rumor_channel_id is None:
        await interaction.response.send_message("⚠️ No rumor channel set. Use `/set_rumor_channel` first.", ephemeral=True)
        return
    
    channel = bot.get_channel(rumor_channel_id)
    if not channel:
        await interaction.response.send_message("⚠️ Rumor channel is invalid. Please reset it.", ephemeral=True)
        return

    await channel.send(f"🕵️‍♂️ Rumor: {text}")
    await interaction.response.send_message("✅ Test rumor sent!", ephemeral=True)

### **Error Handling for Permission Issues**
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("🚫 You don't have permission to use this command.", ephemeral=True)
    else:
        raise error

# Run the bot
TOKEN = "MTM0OTkyODY3NTIwNTcwOTkzNA.GQIp8u.6HUh5v9OxdwL0naBpnGmrLUFn4aDty1hiyGo8U"
bot.run(TOKEN)