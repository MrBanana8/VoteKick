import discord
from discord.ext import commands
import asyncio
import time

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.voice_states = True
client = commands.Bot(command_prefix='/', intents=intents)

class VoteKickButton(discord.ui.View):
    def __init__(self, embed, ctx, voice_members):
        super().__init__()
        self.embed = embed
        self.ctx = ctx
        self.voice_members = voice_members
        self.accept_users = []
        self.declined_users = []
        self.voted = []

    @discord.ui.button(label="✅ Yes", style=discord.ButtonStyle.green)
    async def vote_yes(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user in self.voted:
            await interaction.response.send_message(f"You've already voted.", ephemeral=True)
        else:
            self.voted.append(interaction.user)
            self.accept_users.append(interaction.user)
            self.embed.set_field_at(0, name=f"✅ for YES: {len(self.accept_users)}", value=f"❌ for NO: {len(self.declined_users)}")
            await interaction.message.edit(embed=self.embed)
            await interaction.response.defer()
            await self.check_votes(interaction)

    @discord.ui.button(label="❌ No", style=discord.ButtonStyle.red)
    async def vote_no(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user in self.voted:
            await interaction.response.send_message(f"You've already voted.", ephemeral=True)
        else:
            self.voted.append(interaction.user)
            self.declined_users.append(interaction.user)
            self.embed.set_field_at(0, name=f"✅ for YES: {len(self.accept_users)}", value=f"❌ for NO: {len(self.declined_users)}")
            await interaction.message.edit(embed=self.embed)
            await interaction.response.defer()
            await self.check_votes(interaction)

    async def check_votes(self, interaction):
        if len(self.voted) == len(self.voice_members):
            if len(self.accept_users) > len(self.declined_users):
                await self.user_to_kick.move_to(None)
                await interaction.channel.send(f"{self.user_to_kick.mention} has been disconnected from {self.user_to_kick.voice.channel.mention} by a vote!")
            else:
                await interaction.channel.send(f"{self.user_to_kick.mention} will not be disconnected, majority voted no.")
            self.stop()

@client.tree.command(name="votekick", description="Vote to kick a user from the voice channel")
async def votekick(interaction: discord.Interaction, user: discord.Member):
    if user == interaction.user:
        await interaction.response.send_message("You cannot vote yourself.",ephemeral=True)
        return
    if user not in interaction.user.voice:
        await interaction.response.send_message("You can only vote someone in your vc",ephemeral=True)
        return
    if interaction.user.voice is None:
        await interaction.response.send_message("You are not in a voice channel!", ephemeral=True)
        return
    voice_members = interaction.user.voice.channel.members

    embed = discord.Embed(
        color=discord.Color.purple(),
        description=f'### Vote by: {interaction.user.mention}\nKick player: {user.mention}\n'
    )
    embed.add_field(name="✅ for YES: 0", value="❌ for NO: 0")

    view = VoteKickButton(embed=embed, ctx=interaction,voice_members=voice_members)

    await interaction.response.send_message(embed=embed, view=view)
    

with open("token.0","r",encoding="utf-8") as f:
    TOKEN = f.read()

client.run(TOKEN)