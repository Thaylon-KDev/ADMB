import discord
import os
import json
from dotenv import load_dotenv
from discord.ext import commands

# Load and get token
load_dotenv()
TOKEN = os.getenv ("DISCORD_TOKEN")

# Set Intents
intents = discord.Intents.default()
intents.members = True

def VerifyUser(user_id):
    if os.path.exists("data.json"):
        with open("data.json") as data:
            converted = json.load(data)
            member_quantity = len(converted['users'])

            if str(user_id) in converted['users']:
                return converted['users'][str(user_id)]
            else:
                converted['users'][str(user_id)] = member_quantity + 1

                with open("data.json", "w") as data:
                    json.dump(converted, data, indent=4)
                return converted['users'][str(user_id)]


bot = commands.Bot(command_prefix="!", intents=intents)

class Formulario_Cadastro(discord.ui.Modal, title="Cadastro"):
    warn = discord.ui.TextDisplay("## Atenção! \n **APELIDOS NÃO SÂO ACEITOS** \n O nome será usado como nick no discord \n max de caracteres totais.")
    fist_name = discord.ui.TextInput(label="Primeiro nome:")
    second_name = discord.ui.TextInput(label="1 ou 2 sobrenomes de preferencia:")

    async def on_submit(self, interaction: discord.Interaction):
        new_second_name = self.second_name.value.strip()


        name_parts = self.second_name.value.split()
        if len(name_parts) >= 2:
            new_second_name = f"{name_parts[0]} {name_parts[1][0].upper()}."

        complete_name = f"{self.fist_name.value.replace(" ", "")} {new_second_name.strip()}"

        role_ADS = discord.utils.get(interaction.user.roles, name="ADS")
        role_CD = discord.utils.get(interaction.user.roles, name="CD")
        
        # Set User role wyth ternary
        user_role = "ADS" if role_ADS else "CD" if role_CD else ""
        
        await interaction.user.edit(nick=f"{complete_name} | {user_role}")
        await interaction.response.send_message("Obrigado pelo tempo dedicado!", ephemeral=True)
        await interaction.user.remove_roles(discord.utils.get(interaction.guild.roles, name="No Name"))
        await interaction.message.delete()

class Botão_Identificar(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    @discord.ui.button(label="Me Identificar", custom_id="identify_button",style=discord.ButtonStyle.green)
    async def identificar(self, interaction: discord.Interaction, button):
        await interaction.response.send_modal(Formulario_Cadastro())

# Events
@bot.event
async def on_ready():
    print(f"Connected as {bot.user}")

@bot.event
async def on_member_join(member: discord.Member):

    user_index = VerifyUser(member.id)
    await member.edit(nick=f"User#{user_index:04d}")

    # Bot send identify message
    bot_channel: discord.TextChannel = member.guild.get_channel(1563958013663121651)
    if bot_channel:
       await bot_channel.send(f"Olá, {member.mention}", view=Botão_Identificar())
       
    await member.add_roles(discord.utils.get(member.guild.roles, name="No Name"))

# Persist Button
async def setup_hook():
    bot.add_view(Botão_Identificar())
bot.setup_hook = setup_hook

# Run Bot
bot.run(TOKEN)