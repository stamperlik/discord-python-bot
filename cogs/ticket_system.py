import discord
from discord.ext import commands

TICKET_CATEGORY_ID = 123456789012345678  # Replace with your category ID
SUPPORT_ROLE_ID = 987654321098765432     # Replace with your support role ID
LOG_CHANNEL_ID = 112233445566778899      # Replace with your log channel ID

class TicketDropdown(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="General Support", value="general", description="Need general help?"),
            discord.SelectOption(label="Bug Report", value="bug", description="Report a bug or issue."),
            discord.SelectOption(label="Feature Request", value="feature", description="Suggest a new feature.")
        ]
        super().__init__(placeholder="Select a ticket category", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        guild = interaction.guild
        category = discord.utils.get(guild.categories, id=TICKET_CATEGORY_ID)
        channel_name = f"ticket-{interaction.user.name}".replace(" ", "-").lower()

        # Prevent duplicate tickets
        if discord.utils.get(guild.text_channels, name=channel_name):
            await interaction.response.send_message("❗ You already have a ticket open.", ephemeral=True)
            return

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            interaction.user: discord.PermissionOverwrite(view_channel=True),
            guild.get_role(SUPPORT_ROLE_ID): discord.PermissionOverwrite(view_channel=True),
        }

        ticket_channel = await guild.create_text_channel(
            name=channel_name,
            category=category,
            overwrites=overwrites,
            topic=f"{interaction.user.name} - {self.values[0]}"
        )

        await ticket_channel.send(
            embed=discord.Embed(
                title="🎫 New Ticket",
                description=f"{interaction.user.mention}, thank you! A staff member will assist you shortly.\n\n"
                            f"**Category:** {self.values[0].capitalize()}",
                color=discord.Color.green()
            )
        )

        await interaction.response.send_message(f"✅ Ticket created: {ticket_channel.mention}", ephemeral=True)

        log = guild.get_channel(LOG_CHANNEL_ID)
        if log:
            await log.send(f"📩 Ticket opened by {interaction.user.mention} in {ticket_channel.mention} ({self.values[0]})")

class TicketView(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(TicketDropdown())

class TicketSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="ticket")
    async def ticket(self, ctx):
        embed = discord.Embed(
            title="📩 Create a Ticket",
            description="Need help? Choose a category below to create a support ticket.",
            color=discord.Color.blurple()
        )
        embed.set_footer(text="Your support team is here to help!")
        await ctx.send(embed=embed, view=TicketView())

async def setup(bot):
    await bot.add_cog(TicketSystem(bot))
