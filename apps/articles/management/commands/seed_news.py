import os
import random
from datetime import timedelta
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.utils.text import slugify
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont

from apps.core.models import CustomUser
from apps.articles.models import Article, Category, Comment, ArticleView
from apps.newsletter.models import NewsletterSubscriber


def create_banner_image(title, category_name, bg_color):
    """
    Generates a crisp, editorial high-resolution 16:9 banner image
    using Pillow, complete with subtle gradient and title branding.
    """
    width, height = 1280, 720
    image = Image.new("RGB", (width, height), color=bg_color)
    draw = ImageDraw.Draw(image)

    # Subtle gradient overlay at bottom
    for i in range(250):
        alpha = int((i / 250) * 180)
        draw.line([(0, height - 250 + i), (width, height - 250 + i)], fill=(15, 23, 42, alpha))

    # Grid / aesthetic lines
    draw.line([(60, 60), (width - 60, 60)], fill=(255, 255, 255, 40), width=2)
    draw.line([(60, height - 60), (width - 60, height - 60)], fill=(255, 255, 255, 40), width=2)

    # Category pill banner
    draw.rectangle([(60, 100), (60 + len(category_name) * 18 + 40, 145)], fill=(255, 255, 255))
    
    # Text (using default font if custom TTF is not available)
    try:
        font_large = ImageFont.load_default(size=42)
        font_cat = ImageFont.load_default(size=20)
    except Exception:
        font_large = ImageFont.load_default()
        font_cat = ImageFont.load_default()

    draw.text((80, 112), category_name.upper(), fill=(15, 23, 42), font=font_cat)

    # Draw headline snippet
    display_title = title if len(title) < 55 else title[:52] + "..."
    draw.text((60, height - 160), display_title, fill=(255, 255, 255), font=font_large)

    # Brand watermark
    draw.text((width - 240, height - 100), "THE CHRONICLE", fill=(200, 200, 200), font=font_cat)

    output = BytesIO()
    image.save(output, format='JPEG', quality=90)
    return ContentFile(output.getvalue(), name=f"{slugify(title)[:40]}.jpg")


class Command(BaseCommand):
    help = "Seeds database with comprehensive, production-grade news articles, categories, users, and comments."

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("Initializing The Chronicle seed data generation..."))

        # 1. Superuser
        admin_email = "admin@chronicle.com"
        admin_user, created = CustomUser.objects.get_or_create(
            email=admin_email,
            defaults={
                'username': 'admin',
                'first_name': 'Alexander',
                'last_name': 'Wright',
                'role': CustomUser.ROLE_ADMIN,
                'job_title': 'Editor-in-Chief & Publisher',
                'bio': 'Alexander Wright is the Editor-in-Chief of The Chronicle, overseeing investigative reporting and global newsroom operations.',
                'is_staff': True,
                'is_superuser': True,
            }
        )
        if created:
            admin_user.set_password("admin123")
            admin_user.save()
            self.stdout.write(self.style.SUCCESS(f"Superuser created: {admin_email} (password: admin123)"))
        else:
            self.stdout.write(f"Superuser already exists: {admin_email}")

        # 2. Staff Writers & Editors
        staff_data = [
            {
                'email': 'elena.rostova@chronicle.com',
                'username': 'elena_rostova',
                'first_name': 'Elena',
                'last_name': 'Rostova',
                'role': CustomUser.ROLE_EDITOR,
                'job_title': 'Senior International Affairs Editor',
                'bio': 'Elena covers geopolitical diplomacy, international summits, and strategic security architectures across Europe and Eurasia.',
                'twitter_handle': '@ElenaRostova',
                'linkedin_url': 'https://linkedin.com/in/elena-rostova',
            },
            {
                'email': 'marcus.vance@chronicle.com',
                'username': 'marcus_vance',
                'first_name': 'Marcus',
                'last_name': 'Vance',
                'role': CustomUser.ROLE_WRITER,
                'job_title': 'Chief Artificial Intelligence & Tech Correspondent',
                'bio': 'Marcus investigates autonomous systems, frontier AI research, semiconductor fabrication, and digital ethics.',
                'twitter_handle': '@MarcusVanceAI',
                'linkedin_url': 'https://linkedin.com/in/marcus-vance',
            },
            {
                'email': 'sarah.chen@chronicle.com',
                'username': 'sarah_chen',
                'first_name': 'Sarah',
                'last_name': 'Chen',
                'role': CustomUser.ROLE_WRITER,
                'job_title': 'Global Markets & Macroeconomics Lead',
                'bio': 'Sarah focuses on monetary policy, central banking, cross-border venture capital, and sustainable energy transitions.',
                'twitter_handle': '@SarahChenEcon',
                'linkedin_url': 'https://linkedin.com/in/sarah-chen',
            },
            {
                'email': 'david.kim@chronicle.com',
                'username': 'david_kim',
                'first_name': 'David',
                'last_name': 'Kim',
                'role': CustomUser.ROLE_WRITER,
                'job_title': 'Sports Analytics & Culture Reporter',
                'bio': 'David covers European football, motorsport telemetry, and modern athletic physiology with data-driven narratives.',
                'twitter_handle': '@DavidKimSports',
                'linkedin_url': 'https://linkedin.com/in/david-kim',
            },
            {
                'email': 'clara.monet@chronicle.com',
                'username': 'clara_monet',
                'first_name': 'Dr. Clara',
                'last_name': 'Monet',
                'role': CustomUser.ROLE_WRITER,
                'job_title': 'Science & Planetary Systems Editor',
                'bio': 'Astrophysicist turned science journalist, Dr. Monet writes on deep space missions, climate modeling, and biotech breakthrough discoveries.',
                'twitter_handle': '@DrClaraMonet',
                'linkedin_url': 'https://linkedin.com/in/clara-monet',
            },
        ]

        authors = [admin_user]
        for data in staff_data:
            user, u_created = CustomUser.objects.get_or_create(
                email=data['email'],
                defaults={
                    'username': data['username'],
                    'first_name': data['first_name'],
                    'last_name': data['last_name'],
                    'role': data['role'],
                    'job_title': data['job_title'],
                    'bio': data['bio'],
                    'twitter_handle': data['twitter_handle'],
                    'linkedin_url': data['linkedin_url'],
                    'is_staff': True,
                }
            )
            if u_created:
                user.set_password("chronicle2026")
                user.save()
            authors.append(user)

        self.stdout.write(self.style.SUCCESS(f"Loaded {len(authors)} staff authors and editors."))

        # 3. Categories & Subcategories
        categories_tree = [
            {
                'name': 'Politics',
                'slug': 'politics',
                'color': 'rose',
                'order': 1,
                'description': 'In-depth reporting on national governance, election campaigns, legislative reform, and global diplomacy.',
                'subcategories': [
                    {'name': 'Global Diplomacy', 'slug': 'global-diplomacy', 'color': 'rose'},
                    {'name': 'Elections & Ballots', 'slug': 'elections-ballots', 'color': 'rose'},
                    {'name': 'Policy & Governance', 'slug': 'policy-governance', 'color': 'rose'},
                ]
            },
            {
                'name': 'Technology',
                'slug': 'technology',
                'color': 'blue',
                'order': 2,
                'description': 'Tracking the acceleration of computing, robotics, cybersecurity, frontier models, and Silicon Valley.',
                'subcategories': [
                    {'name': 'Artificial Intelligence', 'slug': 'artificial-intelligence', 'color': 'blue'},
                    {'name': 'Cybersecurity & Privacy', 'slug': 'cybersecurity-privacy', 'color': 'blue'},
                    {'name': 'Green Tech & Clean Energy', 'slug': 'green-tech-clean-energy', 'color': 'blue'},
                ]
            },
            {
                'name': 'Business',
                'slug': 'business',
                'color': 'emerald',
                'order': 3,
                'description': 'Financial markets, macroeconomic movements, real estate, corporate strategy, and venture investments.',
                'subcategories': [
                    {'name': 'Global Markets', 'slug': 'global-markets', 'color': 'emerald'},
                    {'name': 'Venture & Startups', 'slug': 'venture-startups', 'color': 'emerald'},
                    {'name': 'Macroeconomics', 'slug': 'macroeconomics', 'color': 'emerald'},
                ]
            },
            {
                'name': 'Sports',
                'slug': 'sports',
                'color': 'amber',
                'order': 4,
                'description': 'Comprehensive match analysis, transfer developments, athletic performance, and Olympic competition.',
                'subcategories': [
                    {'name': 'Football / Soccer', 'slug': 'football-soccer', 'color': 'amber'},
                    {'name': 'Formula 1', 'slug': 'formula-1', 'color': 'amber'},
                    {'name': 'Tennis & Major Tours', 'slug': 'tennis-major-tours', 'color': 'amber'},
                ]
            },
            {
                'name': 'Health & Science',
                'slug': 'health-science',
                'color': 'purple',
                'order': 5,
                'description': 'Breakthrough medical research, neuroscience, astrophysics, epidemiological studies, and planetary health.',
                'subcategories': [
                    {'name': 'Biotechnology', 'slug': 'biotechnology', 'color': 'purple'},
                    {'name': 'Space & Astrophysics', 'slug': 'space-astrophysics', 'color': 'purple'},
                    {'name': 'Public Health', 'slug': 'public-health', 'color': 'purple'},
                ]
            },
            {
                'name': 'Culture & Arts',
                'slug': 'culture-arts',
                'color': 'indigo',
                'order': 6,
                'description': 'Critical essays, cinema, architecture, literary spotlights, and transformative artistic movements.',
                'subcategories': [
                    {'name': 'Cinema & Streaming', 'slug': 'cinema-streaming', 'color': 'indigo'},
                    {'name': 'Literature & Books', 'slug': 'literature-books', 'color': 'indigo'},
                    {'name': 'Architecture & Design', 'slug': 'architecture-design', 'color': 'indigo'},
                ]
            },
        ]

        cat_lookup = {}
        for cdata in categories_tree:
            parent_cat, _ = Category.objects.get_or_create(
                slug=cdata['slug'],
                defaults={
                    'name': cdata['name'],
                    'color': cdata['color'],
                    'order': cdata['order'],
                    'description': cdata['description'],
                    'is_featured': True,
                }
            )
            cat_lookup[cdata['slug']] = parent_cat

            for sub in cdata.get('subcategories', []):
                sub_cat, _ = Category.objects.get_or_create(
                    slug=sub['slug'],
                    defaults={
                        'name': sub['name'],
                        'parent': parent_cat,
                        'color': sub['color'],
                        'description': f"Specialized coverage within {parent_cat.name}.",
                        'is_featured': True,
                    }
                )
                cat_lookup[sub['slug']] = sub_cat

        self.stdout.write(self.style.SUCCESS(f"Seeded {len(cat_lookup)} categories and subcategories."))

        # 4. Articles Data
        articles_dataset = [
            # Technology - AI (Hero Lead Story)
            {
                'title': 'The Next Frontier in Reasoning: How New Foundation Models Solve Multi-Step Scientific Inferences',
                'category_slug': 'artificial-intelligence',
                'author_email': 'marcus.vance@chronicle.com',
                'is_featured': True,
                'is_breaking': False,
                'is_editors_pick': True,
                'bg_color': (15, 23, 42),
                'views': 14280,
                'days_ago': 0,
                'tags': ['Artificial Intelligence', 'Frontier Tech', 'Quantum Computing', 'Research'],
                'excerpt': 'As next-generation AI architectures demonstrate autonomous multi-step theorem proving and chemical synthesis simulation, leading laboratories confront profound shifts in computational scientific discovery.',
                'body': """
<p class="lead">Autonomous inference engines have crossed an inflection point. In peer-reviewed trials conducted across international laboratories this week, researchers demonstrated that synthetic neural systems can consistently discover novel chemical synthesis pathways and formulate mathematical proofs spanning hundreds of sequential logic gates.</p>

<h2>The Shift from Pattern Recognition to Systematic Verification</h2>
<p>For nearly a decade, machine learning was defined by predictive pattern completion. When supplied with sufficient corpus volume, neural networks predicted the most probable trajectory of prose or code. However, the introduction of iterative deliberative compute—allowing systems to generate internal test cases, run algorithmic simulations, and prune invalid deduction trees—has transformed model capabilities.</p>

<blockquote>"We are no longer looking at simple language generation. We are looking at autonomous verification loops where the computer critiques its own hypotheses before providing an answer."</blockquote>

<p>According to Dr. Aris Thorne, Director of the Advanced Computational Institute in Zurich, the implications for pharmaceutical pipeline discovery and materials science are difficult to overstate.</p>

<h2>Transforming Drug Discovery Horizons</h2>
<p>Target identification in oncology pipelines historically required five to seven years of wet-lab validation. Under initial benchmark deployments, automated verification systems identified viable small-molecule candidates capable of binding to formerly 'undruggable' protein surfaces in under four months.</p>

<p>Key highlights of the benchmark trials include:</p>
<ul>
    <li><strong>94.2% accuracy</strong> on formalized international mathematical olympiad benchmarks.</li>
    <li><strong>Autonomous synthesis routing</strong> without hallucinated chemical reaction intermediaries.</li>
    <li><strong>Zero-shot translation</strong> of genomic expression profiles into mechanistic drug responses.</li>
</ul>

<h2>Sovereignty, Regulation, and Safety Guarantees</h2>
<p>As capabilities surge, policy leaders across Geneva and Washington are drafting unified standards for biological containment and compute monitoring. The consensus among technical committees emphasizes verifiable compute boundaries without curtailing foundational open-source scientific collaboration.</p>
"""
            },
            # Politics (Breaking News)
            {
                'title': 'Global Climate Coalition Reaches Landmark Accord on Sovereign Loss and Damage Financing Framework',
                'category_slug': 'global-diplomacy',
                'author_email': 'elena.rostova@chronicle.com',
                'is_featured': False,
                'is_breaking': True,
                'is_editors_pick': True,
                'bg_color': (225, 29, 72),
                'views': 9820,
                'days_ago': 0,
                'tags': ['Climate Change', 'Global Diplomacy', 'Policy', 'Econ'],
                'excerpt': 'Following marathon forty-eight-hour closed-door negotiations in Brussels, delegates representing 192 sovereign nations ratified a binding multilateral capitalization instrument.',
                'body': """
<p class="lead">In what multilateral delegates are hailing as the most consequential diplomatic breakthrough in over a decade, negotiators concluded an all-night summit by approving a binding charter to inject $180 billion in direct capital into vulnerable coastal and equatorial states.</p>

<h2>An Unprecedented Sovereign Accord</h2>
<p>The resolution marks the culmination of five years of contentious debates concerning sovereign historical liability and climate adaptation economics. Under the compromise framework ratified this morning, capitalization responsibilities will be distributed across established industrial nations and emerging high-output manufacturing powers according to dynamic economic matrices.</p>

<blockquote>"Today, international solidarity moved from rhetoric to concrete fiscal obligations. We have created a legally enforceable bridge between high-emission economies and those bearing the brunt of atmospheric volatility."</blockquote>

<h2>Operational Timelines and Disbursements</h2>
<p>The first tier of relief funds is scheduled for disbursement in early 2027 under the oversight of an independent oversight council stationed in The Hague. Priority allocations will target resilient coastal infrastructure, sea-wall engineering, and drought-resistant agricultural preservation programs throughout Southeast Asia and Sub-Saharan Africa.</p>
"""
            },
            # Business & Markets (Breaking News)
            {
                'title': 'Central Banks Signal Coordinated Liquidity Stabilization Amid Resilient Labor Markets and Disinflation',
                'category_slug': 'global-markets',
                'author_email': 'sarah.chen@chronicle.com',
                'is_featured': False,
                'is_breaking': True,
                'is_editors_pick': False,
                'bg_color': (5, 150, 105),
                'views': 8450,
                'days_ago': 0,
                'tags': ['Global Economy', 'Federal Reserve', 'Macroeconomics', 'Markets'],
                'excerpt': 'Equity indices and sovereign bond yields surged worldwide following synchronized statements from major central banks outlining disciplined rate normalization trajectories.',
                'body': """
<p class="lead">Global equity benchmarks reached quarterly highs on Thursday as monetary authorities in New York, Frankfurt, and Tokyo signaled that the inflationary turbulence of the post-pandemic cycle has largely abated, making way for sustainable macro stabilization.</p>

<h2>A Balanced Soft Landing Takes Shape</h2>
<p>Despite aggressive tightening cycles throughout 2024 and 2025, underlying corporate balance sheets and household debt ratios maintained surprising equilibrium. Industrial capacity utilization remained steady at 78.4%, while real wage gains matched productivity expansion for three consecutive quarters.</p>

<blockquote>"The dual mandate has been achieved without triggering contractionary shockwaves. Our focus now pivots toward maintaining programmatic equilibrium and managing capital liquidity across institutional credit channels."</blockquote>

<h2>Bond Yields Rebalance Across Maturities</h2>
<p>The benchmark 10-year Treasury note eased by 14 basis points to 3.82%, flattening the long-inverted yield curve and reassuring credit analysts that systemic lending spreads remain fundamentally sound.</p>
"""
            },
            # Health & Science - Space
            {
                'title': 'Orbital Observatories Uncover Atmospheric Chemical Signatures on Terrestrial Exoplanet in Trappist-1 System',
                'category_slug': 'space-astrophysics',
                'author_email': 'clara.monet@chronicle.com',
                'is_featured': True,
                'is_breaking': False,
                'is_editors_pick': True,
                'bg_color': (147, 51, 234),
                'views': 11300,
                'days_ago': 1,
                'tags': ['SpaceX', 'Space Exploration', 'Astrophysics', 'Research'],
                'excerpt': 'Spectroscopic transmission data gathered over twenty-four transit cycles confirms the presence of carbon compounds, water vapor, and nitrogen equilibrium forty light-years from Earth.',
                'body': """
<p class="lead">Deep space transmission spectra gathered by the James Webb Space Telescope and corroborated by the European Southern Observatory have revealed definitive atmospheric signatures around TRAPPIST-1e, an Earth-sized rocky exoplanet orbiting within its host star's habitable corridor.</p>

<h2>Spectroscopic Analysis Decodes Atmospheric Layers</h2>
<p>By measuring minute fluctuations in starlight filtering through the exoplanet's atmosphere during transit events, astrophysicists isolated chemical absorption bands corresponding to carbon dioxide, nitrogen, and distinct water vapor signatures.</p>

<blockquote>"We have spent centuries wondering whether temperate, rocky worlds outside our Solar System could sustain stable, dense atmospheres. Today, the data answers definitively in the affirmative."</blockquote>

<p>While planetary scientists caution that the presence of atmospheric carbon and moisture does not constitute proof of biological activity, it confirms that secondary atmospheres can endure red dwarf flare cycles without being stripped into space.</p>
"""
            },
            # Technology - Green Tech
            {
                'title': 'Solid-State Battery Breakthrough Unlocks 1,000-Kilometer Range for Commercial Electric Mobility',
                'category_slug': 'green-tech-clean-energy',
                'author_email': 'marcus.vance@chronicle.com',
                'is_featured': False,
                'is_breaking': False,
                'is_editors_pick': True,
                'bg_color': (37, 99, 235),
                'views': 6720,
                'days_ago': 1,
                'tags': ['Electric Vehicles', 'Green Tech', 'Innovation', 'Clean Energy'],
                'excerpt': 'Silicon-anode pouch cells demonstrated over 1,200 continuous rapid-charge cycles with less than two percent volumetric degradation, positioning solid-state propulsion for commercial rollout.',
                'body': """
<p class="lead">Automotive engineering took an unprecedented leap forward this week as pilot production validation data for solid-electrolyte battery packs proved capable of delivering over 1,000 kilometers of driving range on a single eight-minute ultra-fast charge.</p>

<h2>Eliminating Volumetric Degradation</h2>
<p>The core innovation revolves around a specialized ceramic-polymer hybrid separator that prevents lithium dendrite propagation—a historical failure point in previous solid-state architectures. By maintaining stable interfacial contact under high mechanical stress, the cells withstand operating temperatures ranging from -30°C to 65°C without requiring heavy thermal cooling loops.</p>

<p>Automakers projecting commercial integration expect vehicle curb weights to drop by an average of 400 kilograms, drastically accelerating consumer parity with internal combustion alternatives.</p>
"""
            },
            # Sports - Formula 1
            {
                'title': 'Tactical Masterclass in Monza: Telemetry Data Explains How Under-Cut Pit Strategy Decided the Italian Grand Prix',
                'category_slug': 'formula-1',
                'author_email': 'david.kim@chronicle.com',
                'is_featured': False,
                'is_breaking': False,
                'is_editors_pick': False,
                'bg_color': (217, 119, 6),
                'views': 5420,
                'days_ago': 2,
                'tags': ['Formula 1', 'Sports', 'Motorsport', 'Analytics'],
                'excerpt': 'An intricate analysis of lap degradation deltas, tire carcass temperatures, and straight-line downforce setups explains how victory was won in the pit lane at the Temple of Speed.',
                'body': """
<p class="lead">Amid the deafening roar of 300,000 tifosi at Autodromo Nazionale Monza, the outcome of the Italian Grand Prix was determined not by a dramatic overtake into the Prima Variante, but by a 2.1-second execution window calculated four laps before the leader pitted.</p>

<h2>Telemetry Breakdown: Sector 2 Superiority</h2>
<p>GPS tracking data reveals that the race-winning car maintained a four-kilometer-per-hour corner-exit advantage through the Lesmos. By running slightly stiffer anti-roll bars, the engineering wall mitigated tire graining on the heavily loaded left-front tire, preserving rubber life for a devastating out-lap on hard compound tires.</p>
"""
            },
            # Politics - Policy
            {
                'title': 'The Digital Sovereign Identity Act: Inside the Legislative Debate Reshaping Online Verification and Data Rights',
                'category_slug': 'policy-governance',
                'author_email': 'elena.rostova@chronicle.com',
                'is_featured': False,
                'is_breaking': False,
                'is_editors_pick': False,
                'bg_color': (225, 29, 72),
                'views': 4300,
                'days_ago': 2,
                'tags': ['Policy', 'Cybersecurity', 'Privacy', 'Elections'],
                'excerpt': 'Lawmakers across bipartisan coalitions are negotiating final compromises on decentralized zero-knowledge identity protocols designed to replace corporate single sign-on monopolies.',
                'body': """
<p class="lead">Under proposed legislation currently undergoing committee markup, citizens will gain access to cryptographic, zero-knowledge verifiable credentials that validate age, residency, and citizenship without revealing underlying personal identity data to third-party tech platforms.</p>

<h2>Privacy Advocates and Enterprise Security Align</h2>
<p>Unlike centralized national identity databases, the zero-knowledge framework relies on client-side mathematical proofs. When logging into an online financial service or verifying age for adult platforms, the user's mobile device provides cryptographic verification that the user meets the criterion without transmitting names, birthdays, or document serial numbers.</p>
"""
            },
            # Business - Venture
            {
                'title': 'Sovereign Wealth Funds Pivot Toward Deep Tech Infrastructure as Venture Valuations Stabilize',
                'category_slug': 'venture-startups',
                'author_email': 'sarah.chen@chronicle.com',
                'is_featured': False,
                'is_breaking': False,
                'is_editors_pick': True,
                'bg_color': (5, 150, 105),
                'views': 6120,
                'days_ago': 3,
                'tags': ['Venture Capital', 'Global Economy', 'Startups', 'Markets'],
                'excerpt': 'With speculative software multiples giving way to balance sheet rigor, state-backed capital vehicles are funding multi-billion-dollar semiconductor foundries and orbital logistics networks.',
                'body': """
<p class="lead">A profound structural shift is remaking global private capital. Over $45 billion in sovereign reserves from the Gulf, Scandinavia, and Singapore was reallocated into capital-intensive deep tech initiatives during the past three fiscal quarters, surpassing software-as-a-service investments for the first time on record.</p>

<h2>Capital Expenditure Over Quick Turnarounds</h2>
<p>The appetite for ten-year horizon infrastructure projects—such as extreme ultraviolet lithography research, nuclear small modular reactors (SMRs), and quantum cryptography cables—reflects broader geopolitical priorities surrounding national supply chain resilience.</p>
"""
            },
            # Health - Biotech
            {
                'title': 'Targeted Epigenetic Reprogramming Reverses Cellular Aging Markers in Primate Trial Benchmarks',
                'category_slug': 'biotechnology',
                'author_email': 'clara.monet@chronicle.com',
                'is_featured': False,
                'is_breaking': False,
                'is_editors_pick': True,
                'bg_color': (147, 51, 234),
                'views': 7890,
                'days_ago': 3,
                'tags': ['Biotech', 'Medicine', 'Research', 'Health'],
                'excerpt': 'By selectively activating Yamanaka transcriptional factors via targeted lipid nanoparticle delivery, scientists restored youthful methylation patterns in aged vascular tissue.',
                'body': """
<p class="lead">In a landmark study published in the journal Nature Biotechnology, scientists at the Cambridge Regenerative Biology Institute demonstrated that pulsed cellular reprogramming can erase decades of epigenetic damage without inducing oncogenic pluripotency.</p>

<h2>Restoring Vascular Elasticity</h2>
<p>Treated primate cohorts exhibited a 35% reduction in arterial stiffness and significant improvements in cardiovascular stroke volume. Cellular senescence markers in renal tissue dropped to baseline levels characteristic of organisms half their biological age.</p>
"""
            },
            # Culture - Architecture
            {
                'title': 'The Biophilic Metropolis: How Timber Skyscrapers and Living Facades Are Redefining Modern Urbanism',
                'category_slug': 'architecture-design',
                'author_email': 'david.kim@chronicle.com',
                'is_featured': False,
                'is_breaking': False,
                'is_editors_pick': False,
                'bg_color': (79, 70, 229),
                'views': 3820,
                'days_ago': 4,
                'tags': ['Architecture', 'Urbanism', 'Climate Change', 'Design'],
                'excerpt': 'From Scandinavia to Tokyo, cross-laminated timber towers are sequestering carbon while creating breathable microclimates in high-density downtown districts.',
                'body': """
<p class="lead">The age of cold steel and reflective glass curtain walls is giving way to warm, structural mass timber. Architects worldwide are embracing engineered wood not merely as a decorative accent, but as the foundational load-bearing skeleton for thirty-story high-rises.</p>

<h2>Engineering with Living Materials</h2>
<p>Cross-laminated timber (CLT) panels offer fire resistance comparable to reinforced concrete while trapping thousands of metric tons of sequestered atmospheric carbon within urban skylines for centuries. Coupled with rainwater-irrigated living facades, these structures lower local urban heat island temperatures by up to four degrees Celsius.</p>
"""
            },
            # Sports - Football
            {
                'title': 'The Continental Champions League Revamp: Tactical Innovations Dominating European Football',
                'category_slug': 'football-soccer',
                'author_email': 'david.kim@chronicle.com',
                'is_featured': False,
                'is_breaking': False,
                'is_editors_pick': False,
                'bg_color': (217, 119, 6),
                'views': 5100,
                'days_ago': 4,
                'tags': ['World Cup', 'Football', 'Sports', 'Analytics'],
                'excerpt': 'How fluid 3-2-4-1 build-up structures, inverted wingbacks, and automated offside optical tracking are producing unprecedented tactical sophistication across European stadiums.',
                'body': """
<p class="lead">European club football has entered a tactical renaissance. The rigid positional lines of the past decade have dissolved into hyper-fluid structures where nominal center-backs pivot into midfield orchestrators and wingers operate as deep creators.</p>
"""
            },
            # Technology - Cybersecurity
            {
                'title': 'Post-Quantum Cryptography: Global Financial Networks Begin Phased Migration to Lattice-Based Ciphers',
                'category_slug': 'cybersecurity-privacy',
                'author_email': 'marcus.vance@chronicle.com',
                'is_featured': False,
                'is_breaking': False,
                'is_editors_pick': False,
                'bg_color': (37, 99, 235),
                'views': 4900,
                'days_ago': 5,
                'tags': ['Cybersecurity', 'Quantum Computing', 'Privacy', 'Innovation'],
                'excerpt': 'With practical quantum decryption horizons closing, major interbank messaging protocols have commenced live testing of NIST-standardized crystal-kyber encryption algorithms.',
                'body': """
<p class="lead">The global banking infrastructure is racing against time. Facing the prospect of quantum computers capable of shattering classical RSA and elliptic-curve cryptography within the next decade, international clearing houses have begun rolling out lattice-based key exchange protocols across core transactional pipelines.</p>
"""
            },
            # Entertainment - Cinema
            {
                'title': 'The Renaissance of Practical Effects: Why Modern Cinephiles Are Rejecting CGI Overkill for In-Camera Mastery',
                'category_slug': 'cinema-streaming',
                'author_email': 'david.kim@chronicle.com',
                'is_featured': False,
                'is_breaking': False,
                'is_editors_pick': False,
                'bg_color': (79, 70, 229),
                'views': 3210,
                'days_ago': 5,
                'tags': ['Cinema', 'Culture', 'Arts', 'Entertainment'],
                'excerpt': 'A new generation of visionary directors is reviving large-format 70mm cinematography, physical miniature construction, and live pyrotechnics to capture tangible cinematic gravity.',
                'body': """
<p class="lead">Audiences have reached saturation with glossy, weightless digital spectacle. Box office returns and festival critical consensus in 2026 demonstrate a resolute embrace of in-camera optical photography, physical stunt choreography, and tangible miniature scale models.</p>
"""
            },
            # Health - Public Health
            {
                'title': 'AI-Powered Genomic Surveillance Detects Emerging Microbial Strains Weeks Before Clinical Outbreaks',
                'category_slug': 'public-health',
                'author_email': 'clara.monet@chronicle.com',
                'is_featured': False,
                'is_breaking': False,
                'is_editors_pick': False,
                'bg_color': (147, 51, 234),
                'views': 4150,
                'days_ago': 6,
                'tags': ['Health', 'Biotech', 'Artificial Intelligence', 'Medicine'],
                'excerpt': 'Metagenomic wastewater sequencing combined with deep predictive phylodynamics provides municipal health authorities with predictive early-warning capabilities.',
                'body': """
<p class="lead">By continuously parsing metagenomic DNA and RNA fragments across urban sanitation networks, researchers can now isolate and forecast pathogenic transmission trajectories up to three weeks before patients present symptoms in emergency departments.</p>
"""
            },
            # Business - Macroeconomics
            {
                'title': 'The Semiconductor Geopolitics: Inside the Multi-Trillion Global Fabrication Re-Shoring Boom',
                'category_slug': 'macroeconomics',
                'author_email': 'sarah.chen@chronicle.com',
                'is_featured': False,
                'is_breaking': False,
                'is_editors_pick': True,
                'bg_color': (5, 150, 105),
                'views': 7340,
                'days_ago': 6,
                'tags': ['Semiconductors', 'Global Economy', 'Frontier Tech', 'Markets'],
                'excerpt': 'As multi-billion-dollar semiconductor fabrication plants in Dresden, Phoenix, and Kumamoto reach commercial yield thresholds, the map of silicon independence is permanently redrawn.',
                'body': """
<p class="lead">The silicon race is no longer just about nanoscale architecture; it is about geographical proximity and sovereign operational continuity. With new extreme ultraviolet fabrication fabs going online simultaneously on three continents, the concentration risk that defined microchip production for forty years is being decisively dismantled.</p>
"""
            },
        ]

        now = timezone.now()
        created_articles = []

        for data in articles_dataset:
            category = cat_lookup.get(data['category_slug'])
            if not category:
                category = cat_lookup['technology']

            author = CustomUser.objects.filter(email=data['author_email']).first() or admin_user
            pub_date = now - timedelta(days=data['days_ago'], hours=random.randint(1, 18), minutes=random.randint(5, 50))

            article, created = Article.objects.get_or_create(
                slug=slugify(data['title']),
                defaults={
                    'title': data['title'],
                    'excerpt': data['excerpt'],
                    'body': data['body'],
                    'category': category,
                    'author': author,
                    'status': Article.STATUS_PUBLISHED,
                    'is_breaking': data.get('is_breaking', False),
                    'is_featured': data.get('is_featured', False),
                    'is_editors_pick': data.get('is_editors_pick', False),
                    'views_count': data.get('views', random.randint(1000, 8000)),
                    'published_at': pub_date,
                    'meta_title': data['title'][:65],
                    'meta_description': data['excerpt'][:155],
                }
            )

            # Set featured image if new or image missing
            if created or not article.featured_image:
                banner = create_banner_image(data['title'], category.name, data['bg_color'])
                article.featured_image.save(banner.name, banner, save=True)

            # Add tags
            for tag_name in data.get('tags', []):
                article.tags.add(tag_name)

            created_articles.append(article)

        self.stdout.write(self.style.SUCCESS(f"Loaded {len(created_articles)} comprehensive editorial articles."))

        # 5. Seed Article Views (for realistic analytics and dashboard metrics)
        view_count = 0
        for article in created_articles:
            # Views today
            for _ in range(random.randint(5, 25)):
                view_time = now - timedelta(hours=random.randint(0, 12), minutes=random.randint(0, 59))
                ArticleView.objects.create(
                    article=article,
                    ip_address=f"192.168.1.{random.randint(10, 240)}",
                    session_key=f"sess_{random.randint(100000, 999999)}",
                    viewed_at=view_time
                )
                view_count += 1

            # Views past few days
            for d in range(1, 5):
                for _ in range(random.randint(3, 15)):
                    view_time = now - timedelta(days=d, hours=random.randint(0, 23))
                    ArticleView.objects.create(
                        article=article,
                        ip_address=f"192.168.1.{random.randint(10, 240)}",
                        session_key=f"sess_{random.randint(100000, 999999)}",
                        viewed_at=view_time
                    )
                    view_count += 1

        self.stdout.write(self.style.SUCCESS(f"Seeded {view_count} article view impression logs for analytics."))

        # 6. Seed Reader Comments (approved and pending)
        comments_pool = [
            ("Julian Vance", "julian.v@oxford.edu", "Exceptional analysis. The distinction between predictive pattern recognition and systematic internal verifiers is the most lucid breakdown of this architectural shift I have read this year.", Comment.STATUS_APPROVED),
            ("Dr. Miriam Thorne", "mthorne@geneva-research.org", "The sovereign financing mechanisms will face strict enforcement hurdles in Q3, but codifying the damage metrics into binding agreements is a monumental precedent.", Comment.STATUS_APPROVED),
            ("Arthur Pendelton", "arthur.p@capital-partners.co", "Remarkable numbers on the semiconductor reshoring. It will be interesting to monitor whether water and clean power grid capacities in Arizona can sustain full three-shift manufacturing operations by 2027.", Comment.STATUS_APPROVED),
            ("Nadia Al-Mansoor", "nadia@techpulse.io", "The solid-state battery energy density benchmarks look promising. Can the authors verify whether commercial warranty liabilities have been established for high-cycle fleets?", Comment.STATUS_APPROVED),
            ("Carlos Mendez", "carlos.m@motorsport-insider.es", "That telemetry graphic on Monza's Lesmo corners explains everything! The under-cut delta was so narrow that even a 0.3 second delay on the wheel-gun would have cost them the race.", Comment.STATUS_APPROVED),
            # Pending comments awaiting moderation in Admin panel
            ("Anonymous Techie", "guest101@proton.me", "First! Great article, but what about smaller open source models? Are they catching up with these multi-step verification capabilities?", Comment.STATUS_PENDING),
            ("Evelyn Brooks", "ebrooks@finance-daily.com", "Holding my breath on central bank coordination until we see the preliminary manufacturing employment numbers next Tuesday.", Comment.STATUS_PENDING),
            ("Liam O'Connor", "liam.oc@dublin-ventures.ie", "Would love to see a follow-up piece specifically examining the supply chain of European cross-laminated timber producers.", Comment.STATUS_PENDING),
        ]

        comments_created = 0
        for i, article in enumerate(created_articles[:6]):
            sample_comments = comments_pool[i % len(comments_pool): (i % len(comments_pool)) + 2]
            for name, email, content, status in sample_comments:
                Comment.objects.create(
                    article=article,
                    name=name,
                    email=email,
                    content=content,
                    status=status,
                    ip_address="127.0.0.1",
                    created_at=now - timedelta(hours=random.randint(1, 48))
                )
                comments_created += 1

        self.stdout.write(self.style.SUCCESS(f"Seeded {comments_created} comments (both approved and pending moderation)."))

        # 7. Seed Newsletter Subscribers
        subscribers_list = [
            'alexandra.m@venturecapital.com',
            'henrik.lindqvist@stockholm-tech.se',
            'maya.patel@biopharma-news.org',
            'kenji.sato@tokyo-institute.jp',
            'rachel.greenberg@ny-times-alumni.com',
            'thomas.becker@berlin-energy.de',
            'claire.dubois@parislaw.fr',
            'daniel.zhang@shanghai-fin.cn',
            'sofia.reyes@buenosaires-eco.ar',
            'samuel.adebayo@nairobi-tech.ke',
        ]
        sub_count = 0
        for email in subscribers_list:
            sub, s_created = NewsletterSubscriber.objects.get_or_create(
                email=email,
                defaults={
                    'is_confirmed': True,
                    'is_active': True,
                    'confirmed_at': now - timedelta(days=random.randint(1, 30))
                }
            )
            if s_created:
                sub_count += 1

        self.stdout.write(self.style.SUCCESS(f"Seeded {sub_count} newsletter subscribers."))
        self.stdout.write(self.style.SUCCESS("✓ Complete! The Chronicle is now seeded with production-grade editorial content."))
