# Chaos Control

# Problem

The overview of my project brings awareness to the negative impacts of system downtime.  Every minute counts when you have an application relying heavily on data centers.  The average cost of system downtime *"across industries was valued at approximately **$5,600 per minute**."*<sup>[[a]](https://www.evolven.com/blog/downtime-outages-and-failures-understanding-their-true-costs.html)</sup> According to a 2019 survey, 25 percent of global enterprise companies *"reported the average hourly downtime cost of their servers as being between **$301,000 - 400,000 USD.**"*<sup>[[b]](https://www.statista.com/statistics/753938/worldwide-enterprise-server-hourly-downtime-cost/)</sup>

### In what ways can system downtime impact a company?
  1. A loss in productivity
  2. A loss in opportunity
  3. Brand Damage
  4. Data Loss


# Solution
The repercussions of outages are critical for companies as more and more businesses are moving online.  Some main causes of system downtime are **system overload, equipment failure, and software failure.** <sup>[[a]](https://www.techrepublic.com/article/10-common-causes-of-downtime-and-how-to-avoid-them/)[[b]](https://www.vxchnge.com/blog/common-causes-of-server-downtime)</sup>  I implement **chaos engineering** principles to focus in on these common causes of outages to find holes in the architecture and decrease outages. 

# System Architecture
- I am leveraging an existing data engineering project called *Scale*, which is a music recommendation engine that recommends songs depending on the instruments in a song.  
<p align="center">
    <img src="./pictures/data_pipeline.png" width="600px"  alt="Scale Data Pipeline" >
</p>
