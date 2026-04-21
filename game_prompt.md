# Game Prompt: Guild & Tavern — Adventurer's Guild Management Strategy Game

## Platform, Engine & Genre

Create a **Windows PC indie strategy/management game** using **Unity (C#)**. The game is a **tavern and adventurer's guild management simulator** with RPG progression, hero leveling, crafting, reputation mechanics, and strategic decision-making.

---

## Visual Style Reference: Graveyard Keeper

The game should closely follow the **Graveyard Keeper** visual style and atmosphere. Key art direction references:

- **Pixel art with depth**: High-quality 2D pixel art sprites rendered in a **top-down / ¾ isometric perspective**, identical to Graveyard Keeper's camera angle. Objects should feel volumetric despite being 2D.
- **Normal maps on sprites**: Every sprite (characters, furniture, buildings, trees) should have hand-painted normal maps to simulate volume and react to dynamic lighting — exactly as Graveyard Keeper does. Use Unity's 2D Lights (URP 2D Renderer) to achieve this.
- **Dynamic ambient lighting**: Time-of-day cycle with smooth color transitions — warm golden tones during the day, cool blue tints at night. Implement via LUT (Look-Up Table) color correction, swapping LUT textures as the day progresses (dawn → morning → noon → evening → dusk → night).
- **Dynamic light sources**: Torches, candles, fireplace, forge glow, and lanterns should cast real-time 2D point/spot lights that interact with sprite normal maps. The tavern should feel warm and alive at night.
- **3D light simulation on 2D sprites**: Sprites "behind" a light source should be illuminated differently than sprites "in front of" it (Graveyard Keeper's vertical-axis distance trick). Implement via custom shaders that calculate light-to-sprite vertical offset.
- **Sprite shadows**: Each object has shadow sprites that rotate based on light source positions (sun + up to 3 dynamic sources). Shadow rotation handled in vertex shaders for performance.
- **Wind animation**: Tree canopies, banners, grass, and wheat fields should sway using vertex deformation shaders — not frame-by-frame animation. The deformation intensity increases toward the top of the sprite (roots stay fixed, tips sway most).
- **Fog / atmosphere**: Layered horizontal fog sprites that create depth. Taller objects (rooftops, treetops) peek above the fog layer.
- **Color palette**: Muted, earthy medieval tones with rich warm highlights (firelight, gold coins, ale). Dark humor undertones in the environment — skulls on shelves, questionable stains, cobwebs in corners.
- **UI style**: Parchment/leather-textured panels, hand-drawn icon style, medieval serif fonts. Consistent with Graveyard Keeper's inventory and menu aesthetic.
- **Character sprites**: 32×32 or 48×48 base size with expressive idle animations (breathing, fidgeting). Each hero class should have a distinct silhouette readable at a glance.
- **Environment tiles**: 16×16 or 32×32 tileset for floors, walls, outdoor terrain. Seamless tiling with variation sprites to avoid repetition.

### Technical Art Pipeline (Unity-Specific)
- Use **Unity Universal Render Pipeline (URP)** with the **2D Renderer** for native 2D lighting support.
- Sprite normal maps as secondary textures on `Sprite-Lit-Default` or custom lit shaders.
- **Shader Graph** for wind deformation, shadow rotation, fog, and LUT color grading.
- **Cinemachine 2D** for smooth camera follow and zone transitions.
- Sprite atlases for performance optimization.

---

## Story & Setting

The player has died in the real world and is reborn into a fantasy realm. With no memory of their past life and nothing to their name, they stumble into a small frontier town and land a humble job as a **tavern keeper at the local Adventurer's Guild**. Starting with a run-down tavern and a handful of rookie heroes, the player must grow the guild into a legendary establishment — attracting powerful adventurers, taking on epic contracts, and managing the fine balance between profit, reputation, and the lives of the heroes who depend on them.

But this is not just a business — there is a greater purpose. To the north, the **Mythril Mines** lie frozen under the dominion of a terrifying **Winter Dragon**. The town has been in decline ever since the beast claimed the mines. The player's ultimate goal is to build a guild powerful enough to assemble an elite party of heroes, equip them with Dragonbane gear, and send them to **slay the Winter Dragon** — liberating the mines and ushering in a **Golden Era** for the entire region.

The guild tavern sits on the outskirts of a **neighboring town** — a bustling medieval settlement the player can visit freely. The town is a key location with its own shops, craftsmen, and market square, providing an alternative to building everything in-house. The road between the tavern and town should feel like a short Graveyard Keeper-style walk through a scenic path (trees, fences, a bridge over a creek).

The tone should match Graveyard Keeper's blend of **dark humor and cozy management** — the world is dangerous and morally gray, but the tavern is a warm refuge. NPCs should have quirky personalities, and quest descriptions should mix grim stakes with dry wit.

---

## Core Gameplay Loop

The game runs on a **day-by-day cycle**. Each day the player manages the tavern, assigns quests, crafts, shops, and makes decisions. At the end of each day, the player **must sleep** to advance time. Sleep is when the world updates: quests resolve, heroes return, shops restock, and new events trigger. There is no way to skip or avoid sleep — it is the core pacing mechanism.

### Daily Flow

**Morning → Evening (Active Phase):**
- Check the quest board for available contracts.
- Assign hero parties to quests.
- Craft equipment or place town orders.
- Visit the town to shop, buy décor, or pick up completed orders.
- Manage rooms, talk to heroes, handle settlement requests.
- Famous NPCs may arrive at the tavern with personal quest requests.

**Night → Sleep (Resolution Phase):**
- The player goes to bed. A **sleep screen / end-of-day summary** shows:
  - Quest progress updates (parties still traveling, parties returning tomorrow, etc.).
  - Room rental income collected.
  - Crafting progress (in-house and town orders advance by one day).
  - Any hero arrivals or departures.
- Time advances to the next morning.

### Quest Duration

Quests are not instant. When a hero party departs, they are **gone for a set number of days** based on quest difficulty. Results only arrive when the party returns.

| Quest Tier | Duration | Notes |
|-----------|----------|-------|
| **Common** | 1 day | Heroes depart in the morning, return the next day after sleep. |
| **Uncommon** | 1–2 days | Slightly longer trips. |
| **Rare** | 2–4 days | Heroes are unavailable for several days. Plan accordingly. |
| **Epic** | 4–7 days | Major expeditions. The tavern feels emptier while they're gone. |
| **Legendary** | 7–10 days | Week-long campaigns. Only send heroes you can afford to lose for that long. |
| **Winter Dragon (Mythic)** | 10–14 days | The final quest. A week and a half of anxious waiting. |

While heroes are on a quest, they cannot be assigned to other quests, cannot use the tavern facilities, and their rooms remain reserved (still generating rent if they're residents). The player must manage their roster carefully — sending too many heroes out at once leaves the guild empty and unable to take new contracts.

### Steps & Gameplay Loop

1. **Receive Contracts** — The quest board **refreshes fully once per week** (every 7 in-game days). At the start of each week, a new batch of contracts appears based on your tavern level and reputation. During the week, the board does not refill on its own — once a quest is taken or expires, it's gone until the next weekly refresh.

   However, **famous NPCs** (nobles, merchants, military commanders, royalty) may visit the tavern **at any time during the week** to personally deliver special contracts. These are hand-delivered quests that bypass the weekly board refresh — they appear when the NPC walks into the tavern and speaks to you directly. Famous NPC quests are typically higher quality and better paying, but come with strings attached (see Quest Expiration below).

2. **Assign Quests to Hero Groups** — Review available hero parties and match them to contracts based on difficulty, party composition, hero levels, and gear quality. You can:
   - **Accept a contract and take a percentage fee** from the reward as the guild's cut.
   - **Negotiate with adventurers** to adjust the guild's cut — push for more profit at the risk of losing heroes to rival guilds.
   - **Delegate to a higher-tier party** for better success odds (but they demand a larger share of the reward).

3. **Manage Outcomes** — After the required number of days, heroes return with results:
   - **Success**: Heroes return with loot, gold, **experience points**, and possibly rare artifacts they can sell to you. Heroes who gain enough XP **level up**, unlocking access to harder quests and improving their stats.
   - **Partial success / Injuries**: Wounded heroes need medical treatment at your tavern. You must pay for their care. Neglecting injured heroes **damages your reputation**.
   - **Failure / Death**: If a hero dies on a quest you assigned, your **reputation drops significantly**, reducing the quality of incoming contracts and the caliber of heroes willing to join your guild.

4. **Upgrade the Tavern** — Spend gold to expand and improve the tavern: more rooms, better facilities, a training yard, a trophy hall, rental rooms for heroes, etc. Higher tavern levels attract stronger heroes and unlock higher-tier contracts.

5. **Rent Rooms to Adventurers** — Heroes passing through need a place to sleep. Rent out rooms in your tavern for nightly income. Resident heroes visit the quest board more frequently, accept quests faster, and are always available when you need to form a party. Rooms can be upgraded for higher rent and better morale bonuses.

6. **Craft & Sell Equipment** — Produce and sell gear to adventurers before they depart on quests, increasing their mission success rate and your profit. You have two paths:
   - **In-house crafting**: Hire your own staff (Alchemist, Weapon Crafter, Armor Crafter) and build crafting stations at the tavern. Higher upfront investment, but no per-item fees and full control.
   - **Town outsourcing**: Walk to the neighboring town and place orders at specialist shops. You provide the materials and pay a crafting fee; they do the work. Faster to get started, but costs more per item long-term.

7. **Visit the Town** — Travel to the neighboring town to buy supplies, furniture, decorations, and ready-made goods. Browse shops, compare prices, and place custom crafting orders. The town is also where you hear rumors, meet potential quest-givers, and recruit new staff for your tavern.

8. **Sleep & Advance** — End the day by going to bed. The world advances, quests progress, heroes return, shops restock, and a new day begins.

### Quest Expiration

Not all quests wait forever. Contracts have **expiration dates** that create urgency and force the player to prioritize.

| Quest Tier | Expiration | Notes |
|-----------|-----------|-------|
| **Common** | 3 days | Quick jobs — if nobody takes them, the townsfolk find someone else. |
| **Uncommon** | 5 days | Moderate urgency. |
| **Rare** | 7 days (1 week) | Expires at the next weekly board refresh. |
| **Epic** | **No expiration** | These contracts are so important they stay on the board until taken. |
| **Legendary / Mythic** | **No expiration** | World-shaking threats don't go away on their own. |
| **Famous NPC personal quests** | **Varies (3–7 days)** | The NPC sets the deadline when they deliver the quest. |

**Expiration Consequences:**
- If a **regular quest** expires untaken, it simply disappears from the board. No penalty — you just missed the opportunity and the gold.
- If a **famous NPC quest** is **accepted but ignored** (not assigned to a party before the deadline), the player suffers a **significant reputation loss**. The NPC feels disrespected and spreads word that your guild is unreliable. The higher the NPC's status, the worse the reputation hit.
- If a famous NPC quest is **declined politely** (rejected at the time of offer), there is only a **minor reputation loss** — it's better to say no upfront than to accept and fail to deliver.
- Repeatedly ignoring or failing famous NPC quests can cause those NPCs to **stop visiting your tavern entirely**, cutting off a source of premium contracts.

### Shop & Crafting Restock Cycle

The sleep/day system also drives the economy's refresh rhythm:

| System | Restock Timing | Notes |
|--------|---------------|-------|
| **Town shops (General Store, Apothecary, etc.)** | Daily (each sleep) | Basic stock refreshes every morning. Rare items rotate weekly. |
| **Market Square (rotating merchants)** | Weekly | New traveling merchants arrive with the weekly quest refresh. |
| **In-house crafting** | Continuous | Crafters work daily. Items complete after their crafting duration (1–3 days depending on tier). Progress advances each sleep. |
| **Town custom orders** | Continuous | Same as in-house — progress advances each sleep. Pick up when ready. |
| **Hero-owned shops (Guild District)** | Daily | Stock updates based on what heroes bring back from quests. |
| **Quest board** | Weekly (full refresh) + famous NPC visits mid-week | Board clears and refills every 7 days. NPCs can add quests any day. |

---

## Hero System

### Hero Classes & Roles

Each hero belongs to one **role** and one **class**:

| Role | Classes | Description |
|------|---------|-------------|
| **Tank** | Warrior, Paladin (with shields) | Absorbs damage, protects the party |
| **Melee DPS** | Rogue, Spearman, Berserker | Close-range damage dealers |
| **Ranged DPS** | Marksman, Mage (Fire), Mage (Water), Mage (Wind) | Long-range damage and elemental attacks |
| **Healer** | Priest, Healer Mage | Restores health, cures ailments |

### Hero Leveling & Progression

Heroes are the living, growing heart of the game. They arrive at your guild at various starting levels and grow stronger through successful quests.

**Experience & Leveling:**
- Heroes earn **XP from every completed quest**. XP scales with quest difficulty.
- XP is **split among all party members** — larger parties mean less XP per person.
- Each level requires progressively more XP (exponential curve).
- **Max hero level: 20** (or higher if balancing allows).

**Level-Up Benefits (per level):**
- +Base stat increases (Health, Attack, Defense, Speed) based on class.
- Every **3 levels**: unlock a **class ability** (e.g., Paladin Lv3 = "Shield Wall", Lv6 = "Holy Light", Lv9 = "Divine Aegis").
- Every **5 levels**: unlock a new **equipment tier slot** (allows equipping higher-tier gear).

**Level Tiers & Quest Access:**

| Hero Level | Tier | Quest Difficulty Access | Notes |
|------------|------|------------------------|-------|
| 1–3 | Rookie | Common quests only | High failure rate on anything harder |
| 4–6 | Seasoned | Common + Uncommon | Can handle basic dungeon crawls |
| 7–9 | Veteran | Up to Rare quests | Reliable, sought-after adventurers |
| 10–13 | Elite | Up to Epic quests | Famous heroes, demand higher pay |
| 14–17 | Champion | Up to Legendary quests | Legendary figures, very expensive |
| 18–20 | Mythic | All quests including World Threats | The best of the best |

**Level-Gated Mechanics:**
- **Quest minimum level**: Each contract specifies a minimum average party level. Sending underleveled heroes dramatically increases failure and death chance.
- **Recommended level**: A "sweet spot" level where success is likely but not guaranteed. Overleveled parties trivialize the quest but earn reduced XP (diminishing returns).
- **Hero recruitment level**: New heroes arriving at your guild have a level range based on your tavern level and reputation. A Level 1 tavern attracts Lv1–3 rookies; a Level 5 fortress attracts Lv10–15 champions.
- **Stat growth by class**: Tanks gain more HP/Defense per level, DPS gain more Attack/Speed, Healers gain more healing power and mana.

**Hero Progression Visibility:**
- XP bar visible on each hero's portrait in the roster.
- Level-up notification with stat gains and new ability unlocks.
- Hero history log: list of completed quests, kills, injuries, and milestones.
- Visual sprite changes at tier thresholds (Rookie heroes look scrappy; Mythic heroes have glowing gear and confident idle animations).

### Hero Attributes
- **Level** (1–20, gained through successful quests)
- **XP / XP to next level**
- **Health / Stamina**
- **Attack / Defense / Speed**
- **Class Abilities** (unlocked at level milestones)
- **Equipment slots**: Weapon, Armor, Accessory, Consumable (potion slot)
- **Morale** — affected by tavern quality, quest outcomes, and how well you treat them

### Party System
- Heroes can **freely form groups of any size** (solo to large raid parties).
- Experience and gold rewards are **split among all party members**.
- Larger parties are safer but earn less XP and gold per person; smaller parties are riskier but level faster and earn more.
- Party composition matters: a group without a healer is far more likely to suffer casualties.
- **Party average level** determines which quests the group can attempt.
- A single high-level hero can carry lower-level allies, but the quest difficulty check uses the **average**, not the max — so balance matters.

---

## Room Rental & Hero Settlement

Heroes don't just visit your guild — they can **live** there. This system creates a growing community around your tavern that feeds directly into quest availability, economy, and late-game progression.

### Tavern Room Rental

Your tavern has rentable rooms that heroes can occupy on a nightly basis.

**Room Types:**

| Room Tier | Unlock | Capacity | Nightly Rent | Morale Bonus | Description |
|-----------|--------|----------|-------------|--------------|-------------|
| **Bunk Bed** | Tavern Lv1 | 1 hero | 5 gold | +0 | A straw mattress and a nail to hang your sword. It's a roof. |
| **Private Room** | Tavern Lv2 | 1 hero | 15 gold | +5 | A real bed, a nightstand, and a door that locks. Luxury. |
| **Comfort Suite** | Tavern Lv3 | 1–2 heroes | 30 gold | +10 | Furnished room with a fireplace, desk, and wardrobe. |
| **Hero's Quarter** | Tavern Lv4 | 1–2 heroes | 50 gold | +15 | Premium room with weapon rack, armor stand, and a balcony view. |
| **Champion's Lodge** | Tavern Lv5 | 1–3 heroes | 100 gold | +25 | The finest room in the house. Trophy wall, private bath, enchanted bed that speeds recovery. |

**Rental Benefits:**
- **Passive income**: Rented rooms generate gold every night automatically.
- **Resident heroes**: Heroes renting a room become "residents" — they visit the quest board **every day** instead of randomly passing through. This means more heroes available for quests at any given time.
- **Faster quest pickup**: Resident heroes accept quest assignments immediately (no waiting for them to wander in).
- **Morale boost**: Better rooms give morale bonuses, improving quest performance and reducing the chance heroes leave for a rival guild.
- **Injury recovery**: Injured heroes recover faster if they have a room (especially Champion's Lodge with its enchanted bed).

**Room Management:**
- The player decides how many rooms to build and at what tier (limited by tavern level and available space).
- Rooms can be upgraded in place (Bunk → Private → Comfort, etc.).
- Heroes choose rooms based on their level and wealth — a Mythic champion won't sleep in a bunk bed.
- If no rooms are available, visiting heroes may leave and not return for several days.

### Hero Settlement — Guild District

As heroes accumulate wealth from successful quests, the most established ones will want to **settle permanently near the guild**. This creates a growing **Guild District** — a small neighborhood of hero-owned buildings adjacent to your tavern.

**How It Works:**

1. **Trigger**: When a hero has earned enough gold (threshold scales with hero level, roughly 500–5,000 gold depending on tier), they approach the player with a request: "I'd like to build a house near the guild."
2. **Player approves a plot**: The Guild District has a limited number of building plots (unlocked as the tavern levels up). The player assigns a plot to the hero.
3. **Hero builds their house**: The hero pays for construction themselves (from their own savings). Construction takes several in-game days. A small house appears on the plot with the hero's banner.
4. **Settled hero benefits**: Once settled, the hero becomes a **permanent guild member**:
   - They **never leave** for a rival guild (loyalty locked).
   - They visit the tavern and check the quest board **multiple times per day** (highest quest frequency).
   - They no longer need a rented room (they have their own house), freeing up tavern space.
   - Their morale baseline increases permanently.

**Hero-Owned Businesses:**

Settled heroes with enough wealth and the right class background can **open their own shops** in the Guild District. These function as additional service providers for the player and other heroes:

| Business Type | Opened By | Function | Player Benefit |
|---------------|-----------|----------|----------------|
| **Weapon Shop** | Settled Warrior, Berserker, or Spearman | Sells weapons to other heroes and the player. Stock based on hero's level and quest loot history. | Alternative gear source. The hero sells items at fair prices (cheaper than town for some items). Player can also sell surplus weapons here. |
| **Armor Shop** | Settled Paladin or Warrior | Sells armor and shields. | Same as above, for armor. |
| **Potion Stall** | Settled Healer Mage or Priest | Sells potions and healing supplies. | Convenient potion source without walking to town. |
| **Artifact Dealer** | Settled Mage (any element) or Marksman with 10+ rare quest completions | Buys and sells rare artifacts, magical essences, and enchanted items. | The best place to trade rare materials. The dealer may have unique artifacts from their own adventures. |
| **Training Ground** | Settled hero Lv15+ (any class) | Offers paid training sessions to lower-level heroes, boosting their XP gain for a fee. | Accelerates hero leveling. The trainer earns gold, the trainee gains bonus XP. |

**Business Mechanics:**
- Hero shops have their own inventory that refreshes based on what the hero finds on quests and what the player sells to them.
- Shop quality scales with the hero's level — a Lv18 Warrior's weapon shop has far better stock than a Lv8 one.
- The player can **buy from** and **sell to** hero-owned shops, creating a local micro-economy.
- Hero businesses attract **additional visiting heroes** from outside the guild — word spreads that your Guild District is a one-stop adventuring hub. This increases the pool of available heroes for quests.
- Settled heroes with businesses still take quests — they run the shop when idle and adventure when assigned.

**Guild District Growth:**

| Tavern Level | Building Plots Available | Notes |
|-------------|------------------------|-------|
| 1–2 | 0 | No settlement possible yet |
| 3 | 2 plots | First heroes can settle. Basic houses only. |
| 4 | 4 plots | Heroes can open businesses. District starts to feel alive. |
| 5 | 6 plots | Full district. Multiple shops, training ground. A small village forms around your guild. |
| Golden Era | 8 plots + expanded district | Post-dragon victory: new premium plots, mythril-tier shops possible. |

**Visual Progression:**
The Guild District is visible on the game map as an area adjacent to the tavern. It starts as empty grass plots and gradually fills with houses, shop signs, and foot traffic as heroes settle. In the Golden Era, the district becomes a bustling mini-village with lanterns, paved paths, and hero banners — a visual testament to the player's success.

---

## Crafting System

### Tavern Staff (Recruitable NPCs)
You can hire specialists who work in your tavern:

**Crafting Staff:**

| Staff Role | Function |
|------------|----------|
| **Alchemist** | Crafts potions (healing, stamina, buff potions) |
| **Weapon Crafter** | Forges weapons (swords, bows, staves, spears, daggers) |
| **Armor Crafter** | Creates armor (plate, leather, robes, shields) |

**Hospitality Staff:**

| Staff Role | Function |
|------------|----------|
| **Chef** | Cooks meals using recipes. Better chef = more dishes on the menu, higher food quality, more gold per meal sold. |
| **Barman** | Serves drinks (ale, mead, wine, specialty cocktails). Better barman = faster service, fancier drinks, higher drink revenue. |
| **Waiter** | Serves food and drinks to seated heroes. More waiters = more guests served per day = more revenue. Without waiters, the Chef and Barman output is wasted. |

All staff members have their own skill levels and can be upgraded over time.

---

## Tavern Food & Drink Business

The tavern isn't just a quest hub — it's a **working restaurant and bar**. Heroes (and townsfolk) come to eat and drink, and every meal and mug of ale earns you gold. This is a major revenue stream that runs parallel to quest management, giving the player a way to earn steady income even on slow quest weeks.

### How It Works

1. **Hire hospitality staff**: Recruit a Chef, Barman, and Waiters. You need at least one Waiter for the kitchen and bar to generate any revenue — someone has to carry the plates.
2. **Acquire recipes**: Recipes determine what your tavern can serve. You start with basic fare (bread, stew, cheap ale). Better recipes = fancier dishes = more gold per serving.
3. **Establish farm supply contracts**: Instead of manually sourcing ingredients, you set up **supply contracts with local farms**. Each contract provides a steady daily delivery of specific ingredients (grain, meat, vegetables, milk, eggs, spices, hops, grapes, etc.) for a fixed weekly fee. No need to forage or micromanage ingredient shopping.
4. **Serve guests**: Every day, heroes in the tavern (residents, visitors, settled heroes popping in) and townsfolk order food and drinks. Revenue is calculated automatically based on: number of guests × menu quality × staff efficiency.
5. **Collect revenue at sleep**: Food and drink income is tallied and added to your gold during the nightly sleep resolution.

### Recipes

Recipes are the key to growing your food and drink business. They unlock new menu items and directly increase revenue per guest.

**How to get recipes:**
- **Buy from the town**: The General Store and a dedicated **Cookbook Merchant** in the Market Square sell recipe scrolls. Basic recipes are cheap; rare and exotic recipes are expensive.
- **Heroes bring them back**: Heroes occasionally find recipe scrolls as quest loot — exotic dishes from distant lands, ancient dwarven brewing techniques, elven herbal teas. These are rare and valuable. Heroes can sell them to you, or you can negotiate for them as part of the guild's quest cut.
- **Unlock through Chef/Barman leveling**: As your Chef and Barman gain experience (they level up over time through daily work), they **invent new recipes** at skill milestones. A master Chef creates signature dishes no recipe scroll can teach.

**Recipe Tiers:**

| Tier | Examples | Revenue per Serving | Unlock Source |
|------|---------|-------------------|---------------|
| **Basic** | Bread & butter, thin stew, cheap ale | 2–5 gold | Available from start |
| **Standard** | Roast meat, hearty stew, house ale, mead | 8–15 gold | Town cookbook merchant, Chef Lv2+ |
| **Fine** | Grilled venison, mushroom pie, spiced wine, honey mead | 20–35 gold | Rare town recipes, quest loot, Chef Lv4+ |
| **Exotic** | Dragon pepper steak, elven moonwine, dwarven fire-brew, enchanted feast | 50–100 gold | Quest loot only, Chef/Barman Lv6+ inventions |
| **Legendary** | Mythril-aged wine, Phoenix roast, Ambrosia | 150–300 gold | Post-Golden Era exclusive recipes, master Chef/Barman inventions |

### Farm Supply Contracts

Instead of buying individual ingredients, the player establishes **ongoing supply contracts** with farms in the region. This keeps the food system streamlined — you manage the business, not the grocery list.

| Contract | Provides | Weekly Cost | Unlocked At |
|----------|---------|-------------|-------------|
| **Grain Farm** | Flour, bread ingredients, hops for ale | 50 gold/week | Tavern Lv1 (available from start) |
| **Livestock Ranch** | Meat, eggs, milk, cheese | 80 gold/week | Tavern Lv2 |
| **Vegetable Garden** | Vegetables, herbs, mushrooms, spices | 60 gold/week | Tavern Lv2 |
| **Vineyard** | Grapes, wine base, fruit | 100 gold/week | Tavern Lv3 |
| **Exotic Imports** | Rare spices, foreign ingredients, specialty items | 200 gold/week | Tavern Lv4 |
| **Royal Provisioner** | Premium ingredients for legendary recipes | 400 gold/week | Tavern Lv5 / Golden Era |

**Contract mechanics:**
- Contracts are set up once and auto-renew weekly. The fee is deducted automatically during the weekly quest board refresh.
- You can cancel or upgrade contracts at any time.
- Higher-tier contracts unlock higher-tier recipes (you can't cook exotic dishes without exotic ingredients).
- If you can't afford the weekly fee, the contract pauses and your menu shrinks to whatever ingredients you still have access to.

### Revenue Scaling

Food and drink revenue scales with multiple factors:

- **Number of guests per day**: More heroes in the tavern (residents, visitors, settled heroes, townsfolk) = more orders. Room rentals and the Guild District directly feed this.
- **Menu variety**: More recipes on the menu = each guest spends more (they order appetizer + main + drink instead of just ale).
- **Staff quality**: Higher-level Chef/Barman produce better food faster. Higher-level Waiters serve more guests per day.
- **Number of Waiters**: Each Waiter can serve a limited number of tables. More Waiters = more guests served = more revenue. This is the bottleneck — a great Chef is useless if there's nobody to carry the plates.
- **Tavern appeal**: Better décor and furniture make guests stay longer and order more.

This system rewards investment: hiring better staff, acquiring rare recipes, and upgrading farm contracts all compound into a growing daily income stream that can eventually rival or exceed quest revenue.

### Crafting Materials

**Basic materials** (purchased from merchants or gathered):
- **Iron** — for weapons and heavy armor
- **Leather** — for light armor and accessories
- **Wood** — for bows, staves, shields, and furniture
- **Herbs** — for basic potions

**Rare materials** (obtained from heroes after successful quests):
- **Monster parts** — fangs, scales, bones (for enhanced gear)
- **Magical essences** — elemental crystals, enchanted dust (for enchanted weapons/armor)
- **Ancient artifacts** — legendary fragments (for the most powerful equipment)

### Crafting Tiers
1. **Common** — basic iron/leather/wood gear. Modest stat boosts. Usable by Lv1+ heroes.
2. **Uncommon** — requires basic materials + common monster parts. Usable by Lv4+ heroes.
3. **Rare** — requires rare monster parts + magical essences. Usable by Lv7+ heroes.
4. **Epic** — requires ancient artifacts + rare materials. Usable by Lv10+ heroes. Significantly boosts mission success.
5. **Legendary** — requires multiple ancient artifacts. Usable by Lv14+ heroes. Game-changing equipment.

### In-House vs. Town Crafting — Strategic Choice

The player always has two ways to get crafted goods:

| Approach | Pros | Cons |
|----------|------|------|
| **In-house** (hire staff, build stations) | No per-item fee, faster turnaround once built, staff levels up over time | High upfront cost (staff salary + station construction), takes tavern staff slots |
| **Town orders** (visit town craftsmen) | No upfront investment, available from Day 1, access to specialist recipes you can't make in-house | Per-item crafting fee on top of materials, travel time to town, queue wait times |

This creates a meaningful economic decision: early game you rely on the town; mid-to-late game you invest in your own workshops to cut costs and gain independence — or you stay town-dependent and focus purely on the guild management side.

---

## Neighboring Town & Shops

The town is a separate explorable area connected to the tavern by a short walkable path (Graveyard Keeper-style zone transition). The player physically walks their character to the town, browses shops, talks to NPCs, and returns. The town has its own ambient life — townsfolk walking around, a market square with stalls, smoke rising from chimneys.

### Town Shops

| Shop | Owner | What They Sell | Notes |
|------|-------|---------------|-------|
| **General Store** | Grumpy old merchant | Basic crafting materials (iron, leather, wood, herbs), torches, rope, basic supplies | Cheapest source for bulk materials. Stock refreshes daily. |
| **Apothecary** | Eccentric herbalist | Ready-made potions (healing, stamina, antidotes, buff potions), rare herbs, empty vials | Potions cost more than crafting them yourself, but available immediately. |
| **Blacksmith** | Burly dwarven smith | Ready-made common/uncommon weapons and armor, repair services | Also accepts **custom crafting orders** (see below). |
| **Enchanter's Tower** | Mysterious mage | Magical essences, enchantment scrolls, rare/epic ready-made staves and robes | Expensive but the only source for certain magical materials early on. |
| **Furniture & Décor Shop** | Cheerful carpenter | Tables, chairs, shelves, barrels, chandeliers, wall decorations, rugs, banners | Everything you need to furnish and decorate the tavern. Better décor = higher tavern appeal = better heroes. |
| **Market Square (Stalls)** | Rotating merchants | Seasonal goods, rare ingredients, exotic decorations, traveling merchant specials | Stock changes weekly. Occasionally sells unique one-of-a-kind items. |

### Custom Crafting Orders (Town Workshops)

Instead of (or in addition to) hiring your own crafters, you can place **custom orders** at town workshops:

1. **Visit the shop** (Blacksmith, Apothecary, or Enchanter).
2. **Select a recipe** from their catalog (they may have recipes you don't have access to in-house).
3. **Provide the required materials** from your inventory.
4. **Pay the crafting fee** — this is the labor cost on top of materials. Fee scales with item tier and complexity.
5. **Wait for completion** — orders take in-game time. Simple items: a few hours. Complex items: 1–3 days. You get a notification when the order is ready.
6. **Pick up the finished item** at the shop.

**Order Queue**: Each town craftsman has a limited queue (2–3 orders at a time). If the queue is full, you must wait or use a different craftsman.

**Town Craftsman Skill**: Town NPCs have fixed skill levels that don't change. Your in-house staff can eventually surpass them, giving another reason to invest in your own workshops later.

**Exclusive Town Recipes**: Some specialized items can only be ordered in town (e.g., the Enchanter can create items your in-house crafters can't). This keeps the town relevant even in the late game.

### Tavern Décor & Furnishing

Furniture and decorations purchased from the town (or crafted in-house) directly affect gameplay:

| Décor Category | Effect |
|----------------|--------|
| **Tables & Chairs** | Increase tavern capacity (more heroes can visit at once) |
| **Quality Furniture** (oak tables, cushioned chairs) | Boost hero morale while they rest at the tavern |
| **Trophies & Wall Mounts** | Display quest trophies — increases reputation passively |
| **Lighting** (chandeliers, lanterns, candelabras) | Improves tavern ambiance rating |
| **Banners & Rugs** | Cosmetic + small morale boost. Guild banner unlocked at Tavern Lv3. |
| **Functional Stations** (crafting bench, forge, alchemy table) | Required for in-house crafting. Purchased from the carpenter or built with materials. |

Tavern appeal is a hidden stat calculated from total décor quality. Higher appeal attracts better heroes and unlocks certain high-profile quest-givers who refuse to visit a shabby establishment.

---

## Reputation System

Reputation is the core strategic resource. It determines:
- **Quality of incoming contracts** (higher rep = rarer, more profitable quests)
- **Caliber of heroes** who visit your guild (higher rep = stronger, higher-level adventurers)
- **Prices you can negotiate** (higher rep = better deals)
- **Starting level of new recruits** (higher rep = heroes arrive at higher levels)

### Reputation Changes
| Event | Effect |
|-------|--------|
| Successful quest completion | +Reputation (scales with difficulty) |
| Hero levels up at your guild | +Small reputation bonus |
| Hero returns with rare loot | +Small reputation bonus |
| Injured hero treated promptly | +Reputation (heroes spread the word) |
| Injured hero neglected | −Reputation (significant) |
| Hero death on a quest | −Reputation (severe drop) |
| Sending underleveled heroes to dangerous quests | −Reputation (reckless guild master) |
| Accepted famous NPC quest but ignored deadline | −Reputation (severe — NPC spreads word of unreliability) |
| Politely declined a famous NPC quest | −Reputation (minor — better than ignoring) |
| Repeatedly failing/ignoring famous NPC quests | NPC stops visiting the tavern entirely |
| Tavern upgraded | +Reputation |
| Overcharging heroes on gear | −Reputation (minor) |
| Offering fair prices / discounts | +Reputation (minor) |
| Beautifully decorated tavern | +Reputation (passive, based on décor appeal) |
| Hero settles in Guild District | +Reputation (significant — word spreads that heroes want to live at your guild) |
| Hero opens a business | +Reputation (the guild becomes a destination) |
| Well-maintained rental rooms | +Reputation (minor, passive) |
| Serving fine/exotic food and drinks | +Reputation (minor, passive — "best tavern in the region") |

If reputation drops too low, top-tier heroes leave, high-value contracts dry up, and recovery becomes a difficult but achievable challenge.

---

## Tavern Upgrade Path

| Level | Name | Unlocks |
|-------|------|---------|
| 1 | Shabby Shack | Common quests, Lv1–3 rookie heroes, 1 craft staff slot, 1 hospitality staff slot (Barman or Waiter), 2 bunk bed rooms, grain farm contract available |
| 2 | Modest Inn | Uncommon quests, basic crafting station, 2 craft staff slots, 2 hospitality staff slots, Lv1–5 heroes, private rooms unlocked, up to 4 rentable rooms, livestock + vegetable contracts available |
| 3 | Adventurer's Lodge | Rare quests, training yard, 3 craft staff slots, 3 hospitality staff slots, hero recruitment board, Lv3–9 heroes, comfort suites unlocked, up to 6 rooms, vineyard contract available, **2 Guild District plots** |
| 4 | Renowned Guild Hall | Epic quests, enchanting table, 4 craft staff slots, 4 hospitality staff slots, trophy hall, Lv7–15 heroes, hero's quarters unlocked, up to 8 rooms, exotic imports contract available, **4 Guild District plots, hero businesses enabled** |
| 5 | Legendary Fortress | Legendary quests, master forge, 5 craft staff slots, 5 hospitality staff slots, all hero tiers (up to Lv18–20 Mythic), champion's lodge unlocked, up to 10 rooms, royal provisioner contract available, **6 Guild District plots, Winter Dragon quest chain finale unlocked** |

---

## Economy & Balance Guidelines

- **Guild cut**: Default 10–30% of contract reward, negotiable.
- **Hero treatment costs**: Scale with hero level and injury severity.
- **Hero pay expectations**: Higher-level heroes demand a larger share of quest rewards. A Mythic hero won't work for rookie wages.
- **Room rental income**: Passive nightly gold from rented rooms. Higher-tier rooms = more income but higher build cost. A fully occupied Lv5 tavern with 10 rooms generates significant passive income.
- **Food & drink revenue**: Daily income from serving meals and drinks. Scales with guest count, menu quality, staff level, and number of waiters. Early game this is a small supplement; late game with exotic recipes and a full Guild District it becomes a major income stream.
- **Farm supply costs**: Fixed weekly fees for ingredient contracts. Must be balanced against food revenue — canceling contracts shrinks the menu and revenue.
- **Recipe investment**: Buying recipes from town or negotiating them from heroes is an upfront cost that permanently increases daily food revenue. High ROI over time.
- **Hero settlement**: Heroes pay for their own houses (no cost to the player). Hero-owned shops create a local economy that reduces dependence on the town. Settled heroes are free permanent guild members — the long-term payoff for investing in hero development. Settled heroes also eat and drink at the tavern frequently, boosting food revenue.
- **In-house crafting costs**: Materials + staff salary (ongoing). Better staff = faster and higher quality. No per-item fee.
- **Town shop prices**: Ready-made goods cost 1.5–2× the material value (convenience markup). Custom orders cost materials + 30–50% crafting fee.
- **Town vs. in-house break-even**: Hiring your own crafter pays for itself after roughly 15–20 crafted items (varies by tier). This creates a clear investment decision point.
- **Furniture & décor costs**: Scale with quality tier. Basic table = cheap. Ornate chandelier = expensive. Décor is a long-term investment in tavern appeal.
- **Tavern upgrades**: Exponentially increasing cost to pace progression.
- **XP curve**: Early levels are fast (keep players engaged), later levels are slow (create long-term goals).
- **Risk/reward curve**: Low-level parties on hard quests = high failure chance. Proper level matching = steady growth. Greed = potential disaster.
- **Diminishing XP returns**: Overleveled heroes on easy quests earn minimal XP, encouraging the player to push boundaries.

---

## UI Requirements

All UI should follow the **Graveyard Keeper aesthetic** — parchment textures, leather borders, hand-drawn icons, medieval serif fonts, warm candlelit tones.

- **Main screen**: Tavern interior view (2D top-down ¾ isometric, Graveyard Keeper style) showing the bar, tables with heroes eating and drinking, quest board, crafting stations, Chef working in the kitchen, Barman behind the bar, and Waiters moving between tables. Dynamic lighting from fireplace and candles.
- **Quest Board panel**: List of available contracts with difficulty rating, reward, **minimum level requirement**, recommended level, quest type icon, **estimated duration (days)**, and **expiration countdown** (days remaining, or "No Expiration" for Epic/Legendary). Famous NPC quests are highlighted with a golden border and the NPC's portrait.
- **Hero Roster panel**: All available heroes with stats, **level and XP bar**, equipment, class, abilities, and current status (idle, on quest, injured, leveling up).
- **Party Formation panel**: Drag-and-drop or click-to-assign heroes into groups for quests. Shows **party average level** and **success probability estimate** based on level vs. quest difficulty.
- **Kitchen & Bar panel**: Current menu (active recipes), daily revenue breakdown, staff assignments (Chef, Barman, Waiters), recipe book (owned recipes, locked recipes showing how to obtain them).
- **Farm Contracts panel**: Active supply contracts, weekly costs, available upgrades, cancel/renew options. Shows which ingredient tiers are currently supplied.
- **Crafting panel**: Select recipes, assign materials, choose crafter (in-house or town order). Shows **level requirement** for each item.
- **Town Map / Shop panels**: When visiting the town — shop inventories with buy/sell interface, custom order form (select recipe → provide materials → pay fee → confirm), order status tracker showing pending pickups.
- **Tavern Décor panel**: Furniture placement mode — drag-and-drop tables, chairs, decorations, and functional stations into the tavern layout. Shows current tavern appeal rating.
- **Room Management panel**: Overview of all rental rooms — occupancy status, room tier, nightly income, tenant hero info. Upgrade and build new rooms from here.
- **Guild District panel**: Map view of settlement plots — which heroes have settled, what businesses are open, available empty plots. Click a hero's house to see their shop inventory or assign a plot to a requesting hero.
- **Tavern Management panel**: Upgrade options, staff management, finances overview (including room rental income and district economy summary).
- **Reputation & Stats panel**: Current reputation, gold, tavern level, quest history.
- **Hero Detail panel**: Full hero profile — level progression, ability tree, equipment loadout, quest history, injury log.
- **Event Log**: Scrolling feed of quest results, **level-up announcements**, hero arrivals/departures, reputation changes.
- **Day Counter & Sleep Button**: Persistent top-bar element showing current day number, day of the week, and a "Go to Sleep" button. Also shows how many days until the next weekly quest board refresh. The sleep button triggers the end-of-day summary screen.

---

## Technical Requirements

- **Platform**: Windows (standalone .exe build)
- **Engine**: Unity (C#) with **Universal Render Pipeline (URP) 2D Renderer**
- **Resolution**: 1280×720 minimum, scalable to 1920×1080, with fullscreen/windowed toggle
- **Rendering**: URP 2D Lighting, Sprite normal maps, Shader Graph for visual effects (wind, fog, shadows, LUT color grading)
- **Save/Load system**: JSON or SQLite-based save files with multiple save slots
- **No internet or API keys required** — fully offline single-player experience
- **Art style**: Graveyard Keeper-inspired pixel art (32×32 / 48×48 sprites) with normal maps and dynamic 2D lighting
- **Audio**: Tavern ambiance (crackling fire, murmuring patrons, clinking mugs), medieval background music, UI sounds, quest result fanfares, level-up chime. Use free CC0/royalty-free assets initially.
- **Performance target**: 60 FPS on mid-range hardware
- **Input**: Mouse + keyboard. Controller support is a stretch goal.

---

## Main Quest: The Winter Dragon

The overarching narrative goal that drives the entire game forward.

### Background Lore

Deep in the frozen mountains north of town lies the **Mythril Mines** — once the region's greatest source of wealth. Years ago, a colossal **Winter Dragon** descended upon the mines, freezing everything in eternal ice and claiming the caverns as its lair. The town's economy collapsed. Mythril — the rarest and most powerful crafting material in the world — became unobtainable. The town has been in slow decline ever since, and no adventurer party has ever returned from an attempt to challenge the beast.

The player hears whispers about the Winter Dragon from the very beginning — townsfolk mention it, early quest-givers reference the frozen mountains, and the Enchanter in town speaks of mythril with longing. But the dragon is far beyond anything a rookie guild can handle. It becomes the player's long-term purpose: build a guild powerful enough to slay the Winter Dragon and liberate the mines.

### Quest Chain: The Road to the Dragon

The Winter Dragon is not a single quest — it's a **multi-stage quest chain** that unlocks progressively as the player's guild grows. Each stage is a prerequisite for the next.

| Stage | Quest Name | Requirements | Description |
|-------|-----------|--------------|-------------|
| 1 | **Frozen Rumors** | Tavern Lv2, any Rare quest completed | A traveling merchant tells tales of the frozen mines. Investigate the mountain pass — send a scouting party (Lv5+ recommended). They return with proof: dragon tracks and frozen corpses of previous adventurers. |
| 2 | **The Ice Sentinels** | Tavern Lv3, Reputation ≥ 60% | Frost elementals and ice golems guard the outer mines. Send a Veteran party (Lv8+ recommended) to clear the entrance. They return with **Frostbitten Ore** — a hint of what mythril could be. |
| 3 | **Dragon's Breath** | Tavern Lv4, at least one Lv12+ hero | A deeper expedition into the mines encounters the dragon's minions — frost wyrms and corrupted miners. Elite party required (Lv12+ recommended). Survivors bring back **Frozen Dragon Scales** — a crafting material for frost-resistant gear. |
| 4 | **Forging the Dragonbane** | Enchanter + Blacksmith (town or in-house) | Using Frozen Dragon Scales + Ancient Artifacts + Mythril Fragments (found in Stage 3), craft **Dragonbane equipment** — special frost-resistant, dragon-slaying gear. This is a crafting quest, not a combat quest. The player must gather materials and commission (or craft) a full set of Dragonbane gear for the assault party. |
| 5 | **The Winter Dragon** | Tavern Lv5, full Mythic party (Lv18+), Dragonbane gear equipped, Reputation ≥ 80% | The final assault. Send your best party — fully equipped with Dragonbane weapons, armor, and potions — into the heart of the frozen mines to face the Winter Dragon. This is the hardest quest in the game. Party composition, levels, gear, and potions all matter. Failure means heavy casualties and a long recovery. |

### The Final Battle

The Winter Dragon quest (Stage 5) has a **unique success calculation**:
- Base difficulty: Extreme (highest in the game).
- **Required**: At least one Tank, one Healer, and two DPS (melee or ranged). Minimum 4-hero party.
- **Dragonbane gear bonus**: Each piece of Dragonbane equipment on a party member significantly boosts success chance and reduces injury/death risk. A fully Dragonbane-equipped party has the best odds.
- **Frost resistance potions**: Crafted by the Alchemist using Frozen Dragon Scales. Each potion consumed adds a flat survival bonus.
- **Party average level**: Must be 18+ to even attempt. Every level above 18 adds incremental success chance.
- **Failure consequences**: Heroes can die. Reputation takes a massive hit. The dragon is wounded but not killed — the player can attempt again after recovery, and the dragon is slightly weaker on retry (accumulated damage persists).
- **Success**: The Winter Dragon is slain. Cutscene plays. The mines are liberated.

### Victory: The Golden Era

When the Winter Dragon is defeated:

1. **Cinematic moment**: A celebratory cutscene — the frozen mines thaw, mythril veins glitter in the torchlight, the town erupts in celebration. Your guild's banner is raised over the mine entrance. The heroes who slew the dragon become permanent legends (special golden border on their portraits, unique title "Dragonslayer").

2. **The Mythril Mines open**: A new resource location becomes available. Mythril ore can now be mined and delivered to your guild or purchased from the town. Mythril is the ultimate crafting material — it enables a new **Mythril equipment tier** above Legendary.

3. **Town Golden Era**: The town transforms visually and economically:
   - New buildings appear (expanded market, mythril forge, grand library).
   - Shop inventories expand with mythril-tier goods and new luxury décor.
   - New high-profile NPCs arrive (royal emissaries, master enchanters, legendary heroes seeking your guild).
   - Town ambient life increases — more townsfolk, festive decorations, prosperity everywhere.
   - A new passive income stream: the player receives a **percentage of mythril mining revenue** as the guild that liberated the mines.

4. **New quest tier unlocked**: **Mythril-tier quests** — the most dangerous and rewarding contracts in the game, involving threats beyond the dragon (ancient dungeons, demon incursions, rival kingdoms). These are postgame content for players who want to keep pushing.

5. **Mythril Crafting Tier**:
   - **Mythril equipment** (Tier 6, above Legendary) — requires mythril ore + legendary materials. The absolute best gear in the game. Usable by Lv18+ heroes.
   - Mythril weapons glow with a distinctive blue-silver sheen.
   - Only available after the Golden Era begins.

### Postgame (After the Dragon)

The game **does not end** after slaying the Winter Dragon. The player can continue indefinitely:
- Keep leveling heroes, taking on Mythril-tier quests.
- Fully furnish and max out the tavern.
- Collect all achievements.
- Build a roster of all-Mythril-equipped Dragonslayer heroes.
- The Golden Era town continues to evolve with new events and visitors.

The Winter Dragon victory is the **narrative climax** — the moment the player's long journey pays off. Everything after is a victory lap.

---

## Milestone Achievements

Throughout the game, the player earns milestone achievements that track progress toward (and beyond) the main goal:

| Achievement | Condition |
|-------------|-----------|
| **First Steps** | Complete your first quest |
| **Open for Business** | Upgrade tavern to Level 2 |
| **Veteran Guild** | Have a hero reach Level 10 |
| **Dragon's Shadow** | Complete "Frozen Rumors" (Stage 1) |
| **Into the Frost** | Complete "The Ice Sentinels" (Stage 2) |
| **Dragonbane Forged** | Craft a full set of Dragonbane equipment |
| **Dragonslayer** | Defeat the Winter Dragon |
| **Golden Era** | Witness the town's transformation |
| **Mythril Master** | Craft your first Mythril-tier item |
| **Legend of the Realm** | Have a full party of Lv20 Mythril-equipped Dragonslayers |
| **Guild Village** | Have all Guild District plots occupied with settled heroes |
| **Merchant Prince** | Have 3+ hero-owned businesses operating in the Guild District |
| **Master Innkeeper** | Unlock all recipe tiers and serve a Legendary meal |
| **Tavern Tycoon** | Accumulate 100,000 gold |
| **Perfect Reputation** | Maintain max reputation for 30 in-game days |
| **Century of Quests** | Complete 100 quests |
| **Zero Casualties** | Complete 50 quests in a row with no hero deaths |

---

## Design Decisions & Clarifications

These answers resolve all open questions and must be treated as final decisions by every worker in the pipeline.

### 1. Engine: Unity (Final — Non-Negotiable)
**Unity (C#)** is the final engine choice. This is not up for debate. The team has Unity expertise, the project is already specced for Unity URP 2D Renderer, and all technical requirements (Shader Graph, Cinemachine 2D, sprite normal maps) are Unity-specific. Do NOT suggest Godot, Pygame, or any other engine. Use **Unity 6.3 LTS (6000.3.13f1)** installed at `D:\Unity\Editor\6000.3.13f1\`.

### 2. Quest Resolution Formula
Quest success is calculated deterministically with a controlled RNG element:

```
base_success = 50%
level_bonus  = (party_avg_level - quest_min_level) × 5%     (capped at +30%)
gear_score   = sum(equipped_item_tier × 2%) per party member (capped at +20%)
composition  = +10% if party has at least 1 Tank + 1 Healer
                +5% if party has at least 1 Ranged DPS
                +5% if party has at least 1 Melee DPS
potion_bonus = +3% per consumed potion (capped at +15%)
morale_mod   = (avg_party_morale - 50) × 0.2%               (range: -10% to +10%)

total_success = clamp(base_success + level_bonus + gear_score + composition + potion_bonus + morale_mod, 5%, 95%)

Roll 1-100. If roll <= total_success → SUCCESS.
If roll <= total_success + 15 → PARTIAL SUCCESS (injuries, reduced loot).
Otherwise → FAILURE.
```

Death chance on failure: 10% base per hero, reduced by 3% per gear tier, reduced by 5% if a Healer is present. Minimum 2%.

### 3. Hero AI Behavior
Heroes have **limited autonomous behavior** triggered by specific thresholds:

- **Morale < 20**: Hero threatens to leave. Player gets a 3-day warning. If morale isn't raised (better room, successful quest, food), the hero departs.
- **Morale < 10**: Hero leaves immediately at next sleep cycle. No warning.
- **Hero injured + no treatment for 3 days**: Hero leaves and reputation drops.
- **Hero sees another hero die on a quest they were also on**: -15 morale.
- **Hero reaches Level 10+**: May request a better room. If none available, -5 morale per day.
- **Settled heroes**: Never leave (loyalty locked), but morale still affects quest performance.

Everything else is player-triggered — heroes don't pick quests on their own, don't buy gear autonomously, and don't form parties without the player.

### 4. Balancing Approach
All gold values, XP curves, reputation thresholds, and crafting costs in this document are **initial design estimates**. The implementation should:

- Store ALL balance values in a single `GameBalance.cs` ScriptableObject (or JSON config file) — never hardcode numbers.
- Include a debug/cheat panel (editor-only) to adjust values at runtime for playtesting.
- First balancing playtest: after the core loop is functional (quest assignment → resolution → rewards → leveling). This is NOT a launch blocker for the initial build.

### 5. Art Pipeline
- **Pixel art tool**: Aseprite (or any tool the artist prefers — the pipeline is tool-agnostic, output is PNG sprite sheets).
- **Normal maps**: Auto-generated using **Laigter** (free, open-source) as the primary tool. The artist paints 4-directional light maps (top, bottom, left, right) and Laigter merges them into a normal map. Manual touch-up in Aseprite if needed.
- **Sprite format**: Individual PNGs packed into Unity Sprite Atlases via the built-in Sprite Atlas system.
- **For the initial build**: Use placeholder colored rectangles / simple shapes. Art polish comes later.

### 6. Town Ambient Life
- **Townsfolk count**: 8–12 NPC sprites walking fixed patrol paths (waypoint-based, not full AI).
- **Schedules**: No real schedules. NPCs appear during daytime, disappear at night. Simple enable/disable based on time-of-day.
- **Behavior**: Purely decorative. They walk between waypoints, idle at market stalls, and occasionally stop to "chat" (idle animation pair). No interaction with the player beyond visual ambiance.
- **Post-Golden Era**: 4–6 additional NPCs appear to show prosperity. Festive decorations are static sprites swapped in.

### 7. Hero Name & Appearance Generation
- **Names**: Random from a curated pool of ~200 fantasy names (100 male, 100 female), split by cultural flavor (human, dwarven, elven). No procedural generation — hand-authored list in a JSON file.
- **Appearance**: Each hero class has 3–4 base sprite variants (body type / color palette). On spawn, the game picks a random variant + random hair/accessory overlay. This gives visual variety without needing hundreds of unique sprites.
- **Tier visual upgrades**: At Veteran (Lv7), Elite (Lv10), and Mythic (Lv18) thresholds, the hero's sprite swaps to a more impressive variant (shinier armor, glowing effects).

### 8. Difficulty Settings
**Single fixed difficulty** for version 1.0. No difficulty selector. The game's difficulty is self-regulating:
- Send underleveled heroes → harder (more failures, deaths).
- Invest in gear and leveling → easier (higher success rates).
- The player controls their own difficulty curve through risk management.

A difficulty selector (Easy/Normal/Hard affecting quest failure rates, gold multipliers, and death chance) is a **post-1.0 feature** if player feedback requests it.

### 9. Tutorial & Onboarding
- **Day 1 guided tutorial**: A short scripted sequence on the first in-game day. An NPC (the previous guild master, retiring) walks the player through: accepting a quest, assigning a hero, going to sleep, and reading results. Takes ~5 minutes.
- **Contextual tooltips**: Hover tooltips on all UI elements explaining what they do. First time a panel is opened, a brief tooltip overlay highlights key elements.
- **NPC dialogue hints**: The Barman NPC occasionally gives tips in the event log ("You know, heroes fight better when they're well-fed..." → hints at food system).
- **No mandatory tutorial after Day 1**: The player learns by doing. Systems unlock gradually via tavern levels, which naturally paces the learning curve.

### 10. Localization
- **Version 1.0: English only.**
- **Architecture for localization from Day 1**: All player-facing strings must go through a `LocalizationManager` that reads from JSON string tables (key → translated string). No hardcoded UI text in code. This costs almost nothing to implement upfront and makes future localization trivial.
- String table format: `{"key": "value"}` per language file (`en.json`, future `ru.json`, `de.json`, etc.).

---

## Summary

This is a **Graveyard Keeper-styled strategic management game** built in **Unity** where every decision matters. The player must balance greed vs. safety, investment vs. savings, in-house production vs. town outsourcing, and reputation vs. profit. Heroes are not disposable — they **grow, level up, unlock abilities, and become legends** under your management. The neighboring town provides a living economic ecosystem where the player shops, places crafting orders, and furnishes their tavern.

The driving narrative goal is to build a guild powerful enough to **slay the Winter Dragon** — a multi-stage quest chain that demands Mythic-level heroes, Dragonbane equipment, and careful preparation. Victory liberates the Mythril Mines, triggers the **Golden Era** for the town, and unlocks endgame content — but the game continues beyond, letting the player enjoy the fruits of their legendary guild.

The core fantasy: start with nothing, grow a humble tavern into a legendary guild, watch rookie adventurers become Dragonslayers, and know that every triumph and tragedy traces back to your choices.
