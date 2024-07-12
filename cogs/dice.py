import re

import d20

from discord.ext import commands

from game.dice import roll


class VerboseMDStringifier(d20.MarkdownStringifier):
    def _str_expression(self, node):
        return f"**{node.comment or 'Result'}**: {self._stringify(node.roll)}\n**Total**: {int(node.total)}"


class PersistentRollContext(d20.RollContext):
    def __init__(self, max_rolls=1000, max_total_rolls=None):
        super().__init__(max_rolls)
        self.max_total_rolls = max_total_rolls or max_rolls
        self.total_rolls = 0

    def count_roll(self, n=1):
        super().count_roll(n)
        self.total_rolls += 1
        if self.total_rolls > self.max_total_rolls:
            raise d20.TooManyRolls("Too many dice rolled.")


class Dice(commands.Cog):
    def __init__(self, bot):
        self._bot: commands.Bot = bot

    @commands.command(name="roll", aliases=["r"])
    async def roll_cmd(self, context: commands.Context, *, dice: str = "1d20"):
        if self._is_d6_command(dice):
            await self._roll_single_six(context, dice)
        else:
            await self._roll_single(context, dice)

    @commands.command(name="multiroll", aliases=["rr"])
    async def rr(self, context: commands.Context, iterations: int, *, dice):
        await self._roll_many(context, iterations, dice)
        
    @staticmethod
    def _is_d6_command(dice: str) -> bool:
        pattern = r'^\d+\s*[dD]\s*(?:\+\s*\d+)?(?:\s+.+)?$'
        
        if re.match(pattern, dice):
            return True
        
        return False
        
    @staticmethod
    async def _roll_single_six(context: commands.Context, dice: str):
        try:
            roll_result = roll(dice)
            response = f"{context.author.mention}  :game_die:  {roll_result.label_string()}  \n{(roll_result.dice_string())}"
        except ValueError as e:
            response = f"Error in roll: {str(e)}"
        except Exception as e:
            response = f"Unhandled error: {str(e)}"
            
        await context.send(response)
        
    @staticmethod
    async def _roll_single(context: commands.Context, dice: str):
        try:
            roll_result = d20.roll(dice, allow_comments=True, stringifier=VerboseMDStringifier())
            response = f"{context.author.mention}  :game_die:\n{str(roll_result)}"
        except d20.errors.RollSyntaxError as e:
            response = f"Error in roll: {str(e)}"
        except Exception as e:
            response = f"Unhandled error: {str(e)}"
        
        await context.send(response)

    @staticmethod
    async def _roll_many(context: commands.Context, iterations, roll_str):
        if iterations < 1 or iterations > 100:
            return await context.send("Too many or too few iterations.")

        results = []
        ast = d20.parse(roll_str, allow_comments=True)
        roller = d20.Roller(context=PersistentRollContext())

        for _ in range(iterations):
            res = roller.roll(ast)
            results.append(res)

        header = f"Rolling {iterations} iterations..."
        footer = f"{sum(o.total for o in results)} total."

        if ast.comment:
            header = f"{ast.comment}: {header}"

        result_strs = "\n".join(str(o) for o in results)

        out = f"{header}\n{result_strs}\n{footer}"

        if len(out) > 1500:
            one_result = str(results[0])
            out = f"{header}\n{one_result}\n[{len(results) - 1} results omitted for output size.]\n{footer}"

        await context.send(f"{context.author.mention}\n{out}")

    async def cog_before_invoke(self, context: commands.Context):
        await context.message.delete()


async def setup(bot):
    await bot.add_cog(Dice(bot))
