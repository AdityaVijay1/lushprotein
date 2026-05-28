"""Add CUSTOMERS + SHOPIFY_CHECKOUT entities and missing edges to Group1_ERD.drawio."""
from pathlib import Path

path = Path(__file__).resolve().parent.parent / "Group1_ERD.drawio"
text = path.read_text(encoding="utf-8")

insert = """
        <!-- Added to align ERD with STTM: derived CUSTOMERS + logical SHOPIFY_CHECKOUT -->
        <mxCell id="lp-erd-customers" parent="1" style="shape=table;startSize=30;container=1;collapsible=1;childLayout=tableLayout;fixedRows=1;rowLines=0;fontStyle=1;align=center;resizeLast=1;fillColor=#d5e8d4;strokeColor=#82b366;" value="CUSTOMERS (derived)" vertex="1">
          <mxGeometry height="120" width="280" x="3680" y="390" as="geometry" />
        </mxCell>
        <mxCell id="lp-erd-cust-r1" parent="lp-erd-customers" style="shape=tableRow;horizontal=0;startSize=0;swimlaneHead=0;swimlaneBody=0;fillColor=none;collapsible=0;dropTarget=0;points=[[0,0.5],[1,0.5]];portConstraint=eastwest;strokeColor=inherit;top=0;left=0;right=0;bottom=0;" value="" vertex="1">
          <mxGeometry height="30" width="280" y="30" as="geometry" />
        </mxCell>
        <mxCell id="lp-erd-cust-pk" parent="lp-erd-cust-r1" style="shape=partialRectangle;overflow=hidden;connectable=0;fillColor=none;strokeColor=inherit;top=0;left=0;bottom=1;right=0;fontStyle=1" value="PK" vertex="1">
          <mxGeometry height="30" width="30" as="geometry"><mxRectangle height="30" width="30" as="alternateBounds" /></mxGeometry>
        </mxCell>
        <mxCell id="lp-erd-cust-pk-f" parent="lp-erd-cust-r1" style="shape=partialRectangle;overflow=hidden;connectable=0;fillColor=none;align=left;strokeColor=inherit;top=0;left=0;bottom=1;right=0;spacingLeft=6;fontStyle=5" value="customer_id BIGINT NOT NULL" vertex="1">
          <mxGeometry height="30" width="250" x="30" as="geometry"><mxRectangle height="30" width="250" as="alternateBounds" /></mxGeometry>
        </mxCell>
        <mxCell id="lp-erd-cust-r2" parent="lp-erd-customers" style="shape=tableRow;horizontal=0;startSize=0;swimlaneHead=0;swimlaneBody=0;fillColor=none;collapsible=0;dropTarget=0;points=[[0,0.5],[1,0.5]];portConstraint=eastwest;strokeColor=inherit;top=0;left=0;right=0;bottom=0;" value="" vertex="1">
          <mxGeometry height="30" width="280" y="60" as="geometry" />
        </mxCell>
        <mxCell id="lp-erd-cust-r2a" parent="lp-erd-cust-r2" style="shape=partialRectangle;overflow=hidden;connectable=0;fillColor=none;strokeColor=inherit;top=0;left=0;bottom=0;right=0;" value="" vertex="1">
          <mxGeometry height="30" width="30" as="geometry"><mxRectangle height="30" width="30" as="alternateBounds" /></mxGeometry>
        </mxCell>
        <mxCell id="lp-erd-cust-r2b" parent="lp-erd-cust-r2" style="shape=partialRectangle;overflow=hidden;connectable=0;fillColor=none;align=left;strokeColor=inherit;top=0;left=0;bottom=0;right=0;spacingLeft=6;" value="note: aggregated from orders" vertex="1">
          <mxGeometry height="30" width="250" x="30" as="geometry"><mxRectangle height="30" width="250" as="alternateBounds" /></mxGeometry>
        </mxCell>
        <mxCell id="lp-erd-checkout" parent="1" style="shape=table;startSize=30;container=1;collapsible=1;childLayout=tableLayout;fixedRows=1;rowLines=0;fontStyle=1;align=center;resizeLast=1;fillColor=#fff2cc;strokeColor=#d6b656;" value="SHOPIFY_CHECKOUT (logical)" vertex="1">
          <mxGeometry height="120" width="300" x="3680" y="560" as="geometry" />
        </mxCell>
        <mxCell id="lp-erd-chk-r1" parent="lp-erd-checkout" style="shape=tableRow;horizontal=0;startSize=0;swimlaneHead=0;swimlaneBody=0;fillColor=none;collapsible=0;dropTarget=0;points=[[0,0.5],[1,0.5]];portConstraint=eastwest;strokeColor=inherit;top=0;left=0;right=0;bottom=0;" value="" vertex="1">
          <mxGeometry height="30" width="300" y="30" as="geometry" />
        </mxCell>
        <mxCell id="lp-erd-chk-pk" parent="lp-erd-chk-r1" style="shape=partialRectangle;overflow=hidden;connectable=0;fillColor=none;strokeColor=inherit;top=0;left=0;bottom=1;right=0;fontStyle=1" value="PK" vertex="1">
          <mxGeometry height="30" width="30" as="geometry"><mxRectangle height="30" width="30" as="alternateBounds" /></mxGeometry>
        </mxCell>
        <mxCell id="lp-erd-chk-pk-f" parent="lp-erd-chk-r1" style="shape=partialRectangle;overflow=hidden;connectable=0;fillColor=none;align=left;strokeColor=inherit;top=0;left=0;bottom=1;right=0;spacingLeft=6;fontStyle=5" value="checkout_id BIGINT NOT NULL" vertex="1">
          <mxGeometry height="30" width="270" x="30" as="geometry"><mxRectangle height="30" width="270" as="alternateBounds" /></mxGeometry>
        </mxCell>
        <mxCell id="lp-erd-chk-r2" parent="lp-erd-checkout" style="shape=tableRow;horizontal=0;startSize=0;swimlaneHead=0;swimlaneBody=0;fillColor=none;collapsible=0;dropTarget=0;points=[[0,0.5],[1,0.5]];portConstraint=eastwest;strokeColor=inherit;top=0;left=0;right=0;bottom=0;" value="" vertex="1">
          <mxGeometry height="30" width="300" y="60" as="geometry" />
        </mxCell>
        <mxCell id="lp-erd-chk-r2a" parent="lp-erd-chk-r2" style="shape=partialRectangle;overflow=hidden;connectable=0;fillColor=none;strokeColor=inherit;top=0;left=0;bottom=0;right=0;" value="" vertex="1">
          <mxGeometry height="30" width="30" as="geometry"><mxRectangle height="30" width="30" as="alternateBounds" /></mxGeometry>
        </mxCell>
        <mxCell id="lp-erd-chk-r2b" parent="lp-erd-chk-r2" style="shape=partialRectangle;overflow=hidden;connectable=0;fillColor=none;align=left;strokeColor=inherit;top=0;left=0;bottom=0;right=0;spacingLeft=6;" value="not exported as separate file" vertex="1">
          <mxGeometry height="30" width="270" x="30" as="geometry"><mxRectangle height="30" width="270" as="alternateBounds" /></mxGeometry>
        </mxCell>
        <mxCell id="lp-erd-edge-cust" edge="1" parent="1" source="kulL2Lyo68gXv0h54mrN-333" target="lp-erd-cust-pk-f" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;dashed=0;fontFamily=Helvetica;fontSize=11;fontColor=default;endArrow=ERmandOne;endFill=0;startArrow=ERzeroToMany;startFill=0;">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
        <mxCell id="lp-erd-edge-chk" edge="1" parent="1" source="kulL2Lyo68gXv0h54mrN-291" target="lp-erd-chk-pk-f" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;dashed=1;fontFamily=Helvetica;fontSize=11;fontColor=default;endArrow=ERmandOne;endFill=0;startArrow=ERzeroToMany;startFill=0;">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
        <mxCell id="lp-erd-edge-handle" edge="1" parent="1" source="kulL2Lyo68gXv0h54mrN-402" target="kulL2Lyo68gXv0h54mrN-494" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;fontFamily=Helvetica;fontSize=11;fontColor=default;endArrow=ERmandOne;endFill=0;startArrow=ERzeroToMany;startFill=0;">
          <mxGeometry relative="1" as="geometry">
            <Array as="points"><mxPoint x="4520" y="1400" /><mxPoint x="4520" y="3450" /></Array>
          </mxGeometry>
        </mxCell>
        <mxCell id="lp-erd-label-sessions" parent="1" style="text;html=1;strokeColor=none;fillColor=none;align=center;verticalAlign=middle;fontSize=10;fontColor=#666666;fontStyle=2" value="SESSIONS BY REFERRER: standalone (no order FK) — attribution only" vertex="1">
          <mxGeometry x="3200" y="120" width="320" height="40" as="geometry" />
        </mxCell>
"""

marker = "        <mxCell id=\"kulL2Lyo68gXv0h54mrN-849\""
if "lp-erd-customers" not in text:
    text = text.replace(marker, insert + "\n" + marker)

path.write_text(text, encoding="utf-8")
print("Updated Group1_ERD.drawio with CUSTOMERS, SHOPIFY_CHECKOUT, and new edges.")
