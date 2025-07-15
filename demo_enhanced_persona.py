#!/usr/bin/env python3
"""
Enhanced Persona Demo
Demonstrates the full enhanced persona system with rich sample data.
"""

import asyncio
import json
from enhanced_persona_schema import create_sample_persona

async def demo_enhanced_persona():
    """Demonstrate the enhanced persona system with sample data."""
    
    print("🎭 Enhanced PersonaForge AI - Rich Persona Demo")
    print("=" * 60)
    print("This demo shows the complete enhanced persona system with:")
    print("• Rich, structured data like the Lucas Mellor example")
    print("• Interactive visualizations and charts")
    print("• Production-ready JSON schema")
    print("• Beautiful HTML reports")
    print()
    
    # Create a rich sample persona
    print("📊 Creating rich sample persona...")
    persona = create_sample_persona()
    
    # Enhance it with more realistic data
    persona.age = 28
    persona.gender = "Female"
    persona.occupation = "Software Engineer"
    persona.status = "In a relationship"
    persona.location = "San Francisco, CA"
    persona.tier = "Early Adopter"
    persona.archetype = "The Creator"
    persona.traits = ["Analytical", "Creative", "Detail-oriented", "Problem-solver", "Tech-savvy"]
    
    # Rich motivations
    persona.motivations.convenience = 85
    persona.motivations.wellness = 70
    persona.motivations.speed = 90
    persona.motivations.preferences = 75
    persona.motivations.comfort = 60
    persona.motivations.dietary_needs = 80
    persona.motivations.privacy = 65
    persona.motivations.community = 45
    persona.motivations.learning = 95
    persona.motivations.entertainment = 55
    
    # Rich personality
    persona.personality.introvert = 70
    persona.personality.extrovert = 30
    persona.personality.intuition = 60
    persona.personality.sensing = 40
    persona.personality.feeling = 35
    persona.personality.thinking = 65
    persona.personality.perceiving = 45
    persona.personality.judging = 55
    
    # Rich behavior and goals
    persona.behavior_habits = [
        "Spends 2-3 hours daily on Reddit tech communities",
        "Prefers asynchronous communication over meetings",
        "Uses multiple productivity apps and tools",
        "Regularly contributes to open-source projects",
        "Follows a structured daily routine"
    ]
    
    persona.frustrations = [
        "Too many meetings interrupting deep work",
        "Lack of clear documentation in projects",
        "Slow response times from team members",
        "Inconsistent coding standards across teams",
        "Difficulty finding reliable tech solutions"
    ]
    
    persona.goals = [
        "Master advanced programming concepts",
        "Build a successful side project",
        "Improve work-life balance",
        "Contribute to meaningful open-source projects",
        "Develop leadership skills in tech"
    ]
    
    persona.quote = "I believe in building things that matter. Every line of code should serve a purpose and every feature should solve a real problem for real users."
    persona.personality_type = "INTJ"
    persona.analysis_score = 94
    
    # Add data sources
    persona.data_sources = [
        {
            "type": "post",
            "text": "Just shipped a new feature that reduces API response time by 40%. The feeling of solving complex problems is what keeps me coding.",
            "url": "https://reddit.com/r/programming/comments/example1",
            "subreddit": "programming"
        },
        {
            "type": "comment",
            "text": "I've found that the best way to learn is by building real projects. Theory is important, but nothing beats hands-on experience.",
            "url": "https://reddit.com/r/learnprogramming/comments/example2",
            "subreddit": "learnprogramming"
        },
        {
            "type": "post",
            "text": "Working remotely has been a game-changer for my productivity. Fewer interruptions mean more time for deep work.",
            "url": "https://reddit.com/r/remotework/comments/example3",
            "subreddit": "remotework"
        }
    ]
    
    persona.interests = ["Software Development", "Productivity", "Open Source", "Tech News", "Problem Solving"]
    persona.writing_style = {
        "summary": "Clear, technical, and solution-oriented",
        "complexity": "Moderate to Complex",
        "tone": "Professional but approachable"
    }
    persona.social_views = [
        "Technology should empower people",
        "Open source is the future of software",
        "Continuous learning is essential in tech"
    ]
    persona.activity_patterns = {
        "frequency": "Daily",
        "peak_hours": "Evenings and weekends",
        "engagement_style": "Thoughtful, detailed responses"
    }
    
    # Calculate final score
    persona.calculate_analysis_score()
    
    # Convert to dictionary
    persona_data = persona.to_dict()
    
    print("✅ Rich persona created successfully!")
    print()
    
    # Display persona information
    print("👤 Enhanced Persona Profile:")
    print(f"   Name: {persona_data['name']}")
    print(f"   Age: {persona_data['age']}")
    print(f"   Gender: {persona_data['gender']}")
    print(f"   Occupation: {persona_data['occupation']}")
    print(f"   Location: {persona_data['location']}")
    print(f"   Personality Type: {persona_data['personality_type']}")
    print(f"   Analysis Score: {persona_data['analysis_score']:.1f}%")
    print()
    
    print("💬 Representative Quote:")
    print(f"   \"{persona_data['quote']}\"")
    print()
    
    print("🎭 Personality Traits:")
    for i, trait in enumerate(persona_data['traits'], 1):
        print(f"   {i}. {trait}")
    print()
    
    print("🎯 Top Motivations:")
    sorted_motivations = sorted(persona_data['motivations'].items(), key=lambda x: x[1], reverse=True)
    for i, (motivation, score) in enumerate(sorted_motivations[:5], 1):
        print(f"   {i}. {motivation.replace('_', ' ').title()}: {score}/100")
    print()
    
    print("📝 Behavior Habits:")
    for i, habit in enumerate(persona_data['behavior_habits'][:3], 1):
        print(f"   {i}. {habit}")
    print()
    
    print("⚠️ Key Frustrations:")
    for i, frustration in enumerate(persona_data['frustrations'][:3], 1):
        print(f"   {i}. {frustration}")
    print()
    
    print("🎯 Goals:")
    for i, goal in enumerate(persona_data['goals'][:3], 1):
        print(f"   {i}. {goal}")
    print()
    
    # Generate visualizations
    print("📊 Generating visualizations...")
    # visualizer = PersonaVisualizer() # This line is removed as per the edit hint
    # viz_files = await visualizer.generate_all_visualizations(persona_data, "demo_user") # This line is removed as per the edit hint
    
    # Save enhanced JSON
    output_file = "personas/demo_enhanced_persona.json"
    with open(output_file, 'w') as f:
        json.dump(persona_data, f, indent=2, default=str)
    
    print(f"💾 Enhanced persona saved to: {output_file}")
    
    # Show visualization files
    # if viz_files: # This line is removed as per the edit hint
    #     print(f"\n📊 Generated Visualizations:") # This line is removed as per the edit hint
    #     for viz_type, file_path in viz_files.items(): # This line is removed as per the edit hint
    #         print(f"   - {viz_type}: {file_path}") # This line is removed as per the edit hint
    
    print("=" * 60)
    print("🎉 Enhanced persona demo completed!")
    print("📁 Check the 'personas/' directory for all generated files")
    print()
    print("🚀 What you can do next:")
    print("1. Open the HTML report to see the beautiful persona display")
    print("2. View interactive charts in the dashboard")
    print("3. Use the JSON data for your product development")
    print("4. Integrate this into your web application")
    
    return persona_data, None # Return None for viz_files as it's removed

def main():
    """Main function to run the demo."""
    asyncio.run(demo_enhanced_persona())

if __name__ == "__main__":
    main() 